# This is Spark-free module, which is used by both Spark and Ray materializations

import base64
import datetime
import json
import logging
import os
import re
import time
from typing import Optional
from typing import Tuple

from tecton_core.id_helper import IdHelper
from tecton_proto.materialization.job_metadata_pb2 import JobMetadata
from tecton_proto.materialization.job_metadata_pb2 import JobMetadataTableType


try:
    import boto3
    from botocore.errorfactory import ClientError
except ImportError:
    # not available and unused in dataproc
    boto3 = None
    ClientError = None


logger = logging.getLogger(__name__)
# This section of constants should be used purely for ensuring idempotence of spark jobs.
IDEMPOTENCE_KEY_ATTRIBUTE = "idempotence_key"
VALUE_ATTRIBUTE = "value"
TTL_ATTRIBUTE = "ttl"
LAST_UPDATED_ATTRIBUTE = "last_updated"
RUN_ID_PREFIX = "id:"

TTL_DURATION_SECONDS = int(datetime.timedelta(days=60).total_seconds())

JOB_EXEC_PKEY_ATTRIBUTE = "id"
JOB_EXEC_LAST_UPDATED_ATTRIBUTE = "last_updated"
JOB_EXEC_DATA_ATTRIBUTE = "data"
JOB_EXEC_VERSION_ATTRIBUTE = "version"
CONSUMPTION_BUCKET_SIZE = datetime.timedelta(hours=1)  # see ConsumptionConstants.kt


def get_job_exec(materialization_task_params) -> Tuple[JobMetadata, int]:
    if materialization_task_params.job_metadata_table_type == JobMetadataTableType.JOB_METADATA_TABLE_TYPE_GCS:
        return _get_job_exec_gcs(materialization_task_params)
    elif materialization_task_params.job_metadata_table_type == JobMetadataTableType.JOB_METADATA_TABLE_TYPE_DYNAMO:
        return _get_job_exec_dynamo(materialization_task_params)
    else:
        msg = f"Unhandled JobMetadataTableType: {materialization_task_params.job_metadata_table_type}"
        raise Exception(msg)


def _get_job_exec_dynamo(materialization_task_params) -> Tuple[JobMetadata, int]:
    dynamodb = _dynamodb_client(materialization_task_params)
    table = materialization_task_params.job_metadata_table
    attempt_id = IdHelper.to_string(materialization_task_params.attempt_id)
    item = dynamodb.get_item(
        TableName=table,
        Key={JOB_EXEC_PKEY_ATTRIBUTE: {"S": attempt_id}},
        ConsistentRead=True,
    )["Item"]
    version = item[JOB_EXEC_VERSION_ATTRIBUTE]["N"]
    data = JobMetadata()
    data.ParseFromString(item[JOB_EXEC_DATA_ATTRIBUTE]["B"])
    return data, version


def _get_job_exec_gcs(materialization_task_params) -> Tuple[JobMetadata, int]:
    from google.cloud import storage

    table = materialization_task_params.job_metadata_table
    attempt_id = IdHelper.to_string(materialization_task_params.attempt_id)
    matches = re.match("gs://(.*?)/(.*)", f"{table}/{attempt_id}")
    bucket_name, blob_name = matches.groups()
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    item = blob.download_as_string()
    data = JobMetadata()
    data.ParseFromString(item)
    assert blob.generation is not None, (bucket_name, blob_name, blob)
    return data, blob.generation


def update_job_exec(materialization_task_params, updater) -> Optional[JobMetadata]:
    if materialization_task_params.job_metadata_table_type == JobMetadataTableType.JOB_METADATA_TABLE_TYPE_GCS:
        return _update_job_exec_gcs(materialization_task_params, updater)
    elif materialization_task_params.job_metadata_table_type == JobMetadataTableType.JOB_METADATA_TABLE_TYPE_DYNAMO:
        return _update_job_exec_dynamo(materialization_task_params, updater)
    else:
        msg = f"Unhandled JobMetadataTableType: {materialization_task_params.job_metadata_table_type}"
        raise Exception(msg)


def _update_job_exec_dynamo(materialization_task_params, updater) -> Optional[JobMetadata]:
    dynamodb = _dynamodb_client(materialization_task_params)
    table = materialization_task_params.job_metadata_table
    attempt_id = IdHelper.to_string(materialization_task_params.attempt_id)
    num_retries = 100
    for i in range(num_retries):
        try:
            old_data, old_version = _get_job_exec_dynamo(materialization_task_params)
            new_data = updater(old_data)
            if new_data is None:
                return None
            now_seconds = int(time.time())
            dynamodb.put_item(
                TableName=table,
                Item={
                    JOB_EXEC_PKEY_ATTRIBUTE: {"S": attempt_id},
                    JOB_EXEC_LAST_UPDATED_ATTRIBUTE: {"N": str(now_seconds)},
                    JOB_EXEC_DATA_ATTRIBUTE: {"B": new_data.SerializeToString()},
                    JOB_EXEC_VERSION_ATTRIBUTE: {"N": str(int(old_version) + 1)},
                },
                ConditionExpression="#version = :version",
                ExpressionAttributeNames={"#version": JOB_EXEC_VERSION_ATTRIBUTE},
                ExpressionAttributeValues={":version": {"N": str(old_version)}},
            )
            return new_data
        except ClientError as e:
            # Condition failed means we have a conflicting update
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException" and i + 1 < num_retries:
                continue
            else:
                raise e


def _update_job_exec_gcs(materialization_task_params, updater) -> Optional[JobMetadata]:
    from google import api_core
    from google.cloud import storage

    storage_client = storage.Client()
    table = materialization_task_params.job_metadata_table
    attempt_id = IdHelper.to_string(materialization_task_params.attempt_id)
    num_retries = 100
    for i in range(num_retries):
        try:
            old_data, old_version = _get_job_exec_gcs(materialization_task_params)
            new_data = updater(old_data)
            if new_data is None:
                return None
            matches = re.match("gs://(.*?)/(.*)", f"{table}/{attempt_id}")
            bucket_name, blob_name = matches.groups()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(new_data.SerializeToString(), if_generation_match=old_version)
            return new_data
        except api_core.exceptions.PreconditionFailed as e:
            # We had a conflicting update
            continue


def _dynamodb_client(materialization_task_params):
    if os.environ.get("TEST_ONLY_TECTON_DYNAMODB_ENDPOINT_OVERRIDE"):
        return boto3.client(
            "dynamodb",
            endpoint_url=os.environ["TEST_ONLY_TECTON_DYNAMODB_ENDPOINT_OVERRIDE"],
            region_name=materialization_task_params.dynamodb_table_region,
        )

    if materialization_task_params.HasField("dynamodb_cross_account_role_arn"):
        sts_client = boto3.client("sts", region_name=materialization_task_params.dynamodb_table_region)
        if materialization_task_params.dynamodb_cross_account_external_id:
            assumed_role_object = sts_client.assume_role(
                RoleArn=materialization_task_params.dynamodb_cross_account_role_arn,
                RoleSessionName="tecton_materialization",
                ExternalId=materialization_task_params.dynamodb_cross_account_external_id,
            )
        else:
            assumed_role_object = sts_client.assume_role(
                RoleArn=materialization_task_params.dynamodb_cross_account_role_arn,
                RoleSessionName="tecton_materialization",
            )
        credentials = assumed_role_object["Credentials"]
        return boto3.client(
            "dynamodb",
            region_name=materialization_task_params.dynamodb_table_region,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
    elif materialization_task_params.HasField("dbfs_credentials_path"):
        with open(f"/dbfs{materialization_task_params.dbfs_credentials_path}") as f:
            credentials = json.loads(base64.b64decode(f.read()))
            return boto3.client(
                "dynamodb",
                region_name=materialization_task_params.dynamodb_table_region,
                aws_access_key_id=credentials["accessKeyId"],
                aws_secret_access_key=credentials["secretAccessKey"],
                aws_session_token=credentials["sessionToken"],
            )
    else:
        return boto3.client("dynamodb", region_name=materialization_task_params.dynamodb_table_region)
