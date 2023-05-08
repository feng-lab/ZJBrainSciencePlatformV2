from test import client

import pytest

from app.model.response import Response
from app.model.schema import UserResponse


@pytest.mark.parametrize(
    "content_language, message", [("zh_CN", "成功"), ("en_US", "success"), ("invalid language", "成功")]
)
def test_content_language_header(
    logon_root_headers: dict[str, str], content_language: str, message: str
) -> None:
    headers = logon_root_headers | {"Content-Language": content_language}
    r = client.get("/api/getCurrentUserInfo", headers=headers)
    assert r.is_success
    ro = Response[UserResponse](**r.json())
    assert ro.code == 0
    assert ro.message == message


def test_no_content_language_header(logon_root_headers: dict[str, str]) -> None:
    r = client.get("/api/getCurrentUserInfo", headers=logon_root_headers)
    assert r.is_success
    ro = Response[UserResponse](**r.json())
    assert ro.code == 0
    assert ro.message == "成功"
