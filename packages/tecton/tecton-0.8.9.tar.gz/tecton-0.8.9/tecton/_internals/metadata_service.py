import logging
import threading
from typing import Optional

from google.protobuf.empty_pb2 import Empty

import tecton
from tecton._internals.metadata_service_impl.base_stub import BaseStub
from tecton._internals.metadata_service_impl.http_client import PureHTTPStub
from tecton_core import conf


_lock = threading.Lock()
_stub_instance: Optional[BaseStub] = None

logger = logging.getLogger(__name__)


def instance() -> BaseStub:
    if getattr(tecton, "__initializing__"):
        msg = "Tried to initialize MDS during module import"
        raise Exception(msg)
    global _stub_instance
    with _lock:
        if not _stub_instance:
            stub = PureHTTPStub()
            conf._init_metadata_server_config(stub.GetConfigs(Empty()))

            # Only set the global at the end. Otherwise if GetConfigs() fails, we won't try to initialize the configs
            # again if the user retries
            _stub_instance = stub
        return _stub_instance


def close_instance():
    global _stub_instance
    with _lock:
        if _stub_instance:
            _stub_instance.close()
            _stub_instance = None
