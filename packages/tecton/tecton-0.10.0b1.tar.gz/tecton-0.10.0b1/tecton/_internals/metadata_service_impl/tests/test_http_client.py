from unittest import TestCase
from unittest import mock

from google.protobuf.empty_pb2 import Empty

from tecton._internals.metadata_service_impl.auth_lib import InternalAuthProvider
from tecton._internals.metadata_service_impl.request_lib import InternalRequestProvider
from tecton._internals.metadata_service_impl.service_modules import GRPC_SERVICE_MODULES
from tecton_core.metadata_service_impl import error_lib
from tecton_core.metadata_service_impl import http_client
from tecton_core.metadata_service_impl.service_calls import GrpcCall


@mock.patch(
    "tecton._internals.metadata_service_impl.request_lib.InternalRequestProvider.request_url",
    return_value="https://test.tecton.ai/api",
)
@mock.patch("tecton.identities.okta.get_token_refresh_if_needed", lambda: None)
class HttpClientTest(TestCase):
    @mock.patch("tecton_core.metadata_service_impl.http_client._InternalHTTPStub.execute")
    def test_valid_request(self, mock_execute, _):
        """
        Tests the translation of the PureHTTPStub Nop(proto) method to _InternalHTTPStub.execute('Nop', proto).
        """
        expected_grpc_call = GrpcCall(
            "/tecton_proto.metadataservice.MetadataService/Nop", Empty.SerializeToString, Empty.FromString
        )
        mock_execute.return_value = Empty()
        stub = http_client.PureHTTPStub(InternalRequestProvider(InternalAuthProvider()), GRPC_SERVICE_MODULES)
        response = stub.Nop(Empty())
        mock_execute.assert_called_once()
        mock_execute.assert_called_with(expected_grpc_call, Empty(), 300.0)
        assert response == Empty()

    @mock.patch("tecton_core.metadata_service_impl.http_client._InternalHTTPStub.execute")
    def test_timeout_param(self, mock_execute, _):
        """
        Test passing in a timeout to a method called on PureHTTPStub
        """
        expected_grpc_call = GrpcCall(
            "/tecton_proto.metadataservice.MetadataService/Nop", Empty.SerializeToString, Empty.FromString
        )
        mock_execute.return_value = Empty()
        stub = http_client.PureHTTPStub(InternalRequestProvider(InternalAuthProvider()), GRPC_SERVICE_MODULES)
        response = stub.Nop(Empty(), timeout_sec=5.0)
        mock_execute.assert_called_once()
        mock_execute.assert_called_with(expected_grpc_call, Empty(), 5.0)
        assert response == Empty()

    @mock.patch("tecton_core.metadata_service_impl.http_client._InternalHTTPStub.execute")
    def test_invalid_method(self, mock_execute, _):
        """
        Tests error handling of a method called on PureHTTPStub that doesn't map to a valid MetadataService method.
        """
        stub = http_client.PureHTTPStub(InternalRequestProvider(InternalAuthProvider()), GRPC_SERVICE_MODULES)
        with self.assertRaisesRegex(AttributeError, "Nonexistent MetadataService method: InvalidRequestName"):
            stub.InvalidRequestName(Empty())
        mock_execute.assert_not_called()

    @mock.patch("requests.Session.request")
    def test_unauthenticated_request(self, mock_request, _):
        """
        Test when unauthenticated status is returned
        """

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {"status": {"code": error_lib.gRPCStatus.UNAUTHENTICATED.value, "detail": "thedetail"}}

        mock_request.return_value = FakeResponse()
        stub = http_client.PureHTTPStub(InternalRequestProvider(InternalAuthProvider()), GRPC_SERVICE_MODULES)
        with self.assertRaises(PermissionError) as context:
            stub.Nop(Empty())
        assert "Tecton credentials are invalid, not configured, or expired" in str(context.exception)

    @mock.patch("requests.Session.request")
    def test_permission_denied_request(self, mock_request, _):
        """
        Test when permission denied (unauthorized) status is returned
        """

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {"status": {"code": error_lib.gRPCStatus.PERMISSION_DENIED.value, "detail": "thedetail"}}

        mock_request.return_value = FakeResponse()
        stub = http_client.PureHTTPStub(InternalRequestProvider(InternalAuthProvider()), GRPC_SERVICE_MODULES)
        with self.assertRaisesRegex(PermissionError, ".*Insufficient permissions.*"):
            stub.Nop(Empty())

    @mock.patch("requests.Session.request")
    def test_permission_denied_unauthenticated_request(self, mock_request, _):
        """
        Test when permission denied (unauthorized) status is returned
        """

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "status": {
                        "code": error_lib.gRPCStatus.PERMISSION_DENIED.value,
                        "detail": "UNAUTHENTICATED: InvalidToken",
                    }
                }

        mock_request.return_value = FakeResponse()
        stub = http_client.PureHTTPStub(InternalRequestProvider(InternalAuthProvider()), GRPC_SERVICE_MODULES)
        with self.assertRaisesRegex(PermissionError, ".*Insufficient permissions.*"):
            stub.Nop(Empty())

    # TODO: Remove with https://tecton.atlassian.net/browse/TEC-9107
    #  (once the metadata service no longer returns PERMISSION_DENIED when authentication is required but not included)
    @mock.patch("requests.Session.request")
    def test_permission_denied_no_header_request(self, mock_request, _):
        """
        Test when permission denied (unauthorized) status is returned
        """

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {"status": {"code": error_lib.gRPCStatus.PERMISSION_DENIED.value, "detail": "thedetail"}}

        mock_request.return_value = FakeResponse()
        stub = http_client.PureHTTPStub(InternalRequestProvider(InternalAuthProvider()), GRPC_SERVICE_MODULES)
        with self.assertRaisesRegex(PermissionError, ".*Insufficient permissions.*"):
            stub.Nop(Empty())
