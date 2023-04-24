import logging
from typing import TypeVar

import requests
from pydantic import BaseModel

from app.common.config import config
from app.common.exception import ServiceError
from app.common.log import request_id_ctxvar
from app.external.model import (
    DisplayDataResponse,
    DisplayEEGRequest,
    DisplayNeuralSpikeRequest,
    GetEEGChannelsResponse,
    GetFileInfoRequest,
    NeuralSpikeFileInfo,
    NoneResponse,
    Response,
    ResponseCode,
)

logger = logging.getLogger(__name__)

Req = TypeVar("Req", bound=BaseModel)
Resp = TypeVar("Resp", bound=BaseModel)


def do_rpc(api: str, request: Req, response_model: type[Resp]) -> Resp:
    rpc_url = f"http://{config.ALGORITHM_HOST}{api}"
    headers = {config.REQUEST_ID_HEADER_KEY: request_id_ctxvar.get()}

    http_response = requests.post(rpc_url, data=request.json(), headers=headers)

    if http_response.status_code != requests.codes.ok:
        response_type = NoneResponse
    else:
        response_type = Response[response_model]
    response = response_type.parse_obj(http_response.json())
    if response.code != ResponseCode.SUCCESS:
        logger.error(
            f"remote service returns error, code={response.code}, message={response.message}"
        )
        raise ServiceError.remote_service_error(f"远程服务错误: {response.message}")
    return response.data


def display_eeg(request: DisplayEEGRequest) -> DisplayDataResponse:
    return do_rpc("/display/eeg", request, DisplayDataResponse)


def display_neural_spike(request: DisplayNeuralSpikeRequest) -> DisplayDataResponse:
    return do_rpc("/display/neural-spike", request, DisplayDataResponse)


def get_eeg_channels(request: GetFileInfoRequest) -> GetEEGChannelsResponse:
    return do_rpc("/info/eeg/channels", request, GetEEGChannelsResponse)


def get_neural_spike_info(request: GetFileInfoRequest) -> NeuralSpikeFileInfo:
    return do_rpc("/info/neural-spike", request, NeuralSpikeFileInfo)
