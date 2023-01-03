from typing import Callable

import grpc
from app.common.config import config
from app.common.util import T


def grpc_stub(service: type[T]) -> Callable[[], T]:
    def depend_func() -> T:
        service_address = config.get_algorithm_grpc_address()
        with grpc.insecure_channel(service_address) as channel:
            stub = service(channel)
            yield stub

    return depend_func
