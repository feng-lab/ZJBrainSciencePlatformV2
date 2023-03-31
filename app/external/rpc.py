import logging
from typing import TypeVar

import requests
from pydantic import BaseModel

from app.common.config import config
from app.common.exception import ServiceError
from app.common.log import request_id_ctxvar
from app.external.model import DisplayEEGRequest, DisplayEEGResponse, Response, ResponseCode

logger = logging.getLogger(__name__)

Req = TypeVar("Req", bound=BaseModel)
Resp = TypeVar("Resp", bound=BaseModel)


def do_rpc(api: str, request: Req, response_model: type[Resp]) -> Resp:
    rpc_url = f"http://{config.ALGORITHM_HOST}{api}"
    headers = {config.REQUEST_ID_HEADER_KEY: request_id_ctxvar.get()}

    http_response = requests.post(rpc_url, data=request.json(), headers=headers)

    if http_response.status_code != requests.codes.ok:
        logger.error(
            f"remote service error, status_code={http_response.status_code}, content={http_response.content}"
        )
        raise ServiceError.remote_service_error("远程服务错误")
    response = Response[response_model].parse_obj(http_response.json())
    if response.code != ResponseCode.SUCCESS:
        logger.error(
            f"remote service returns error, code={response.code}, message={response.message}"
        )
        raise ServiceError.remote_service_error("远程服务错误")
    return response.data


def display_eeg(request: DisplayEEGRequest) -> DisplayEEGResponse:
    return do_rpc("/eeg/display", request, DisplayEEGResponse)
