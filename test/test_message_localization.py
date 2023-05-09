from test import client

import pytest

from app.model.response import NoneResponse, Response
from app.model.schema import UserResponse


@pytest.mark.parametrize(
    ["locale", "expect_message"],
    [("zh-CN", "成功"), ("en-US", "success"), ("invalid language", "成功")],
)
def test_content_language_header(
    logon_root_headers: dict[str, str], locale: str, expect_message: str
) -> None:
    headers = logon_root_headers | {"Content-Language": locale}
    r = client.get("/api/getCurrentUserInfo", headers=headers)
    assert r.is_success
    ro = Response[UserResponse](**r.json())
    assert ro.code == 0
    assert ro.message == expect_message


def test_no_content_language_header(logon_root_headers: dict[str, str]) -> None:
    r = client.get("/api/getCurrentUserInfo", headers=logon_root_headers)
    assert r.is_success
    ro = Response[UserResponse](**r.json())
    assert ro.code == 0
    assert ro.message == "成功"


@pytest.mark.parametrize(
    ["locale", "expect_message"], [("zh-CN", "用户不存在"), ("en-US", "user cannot be found")]
)
def test_not_found(logon_root_headers: dict[str, str], locale: str, expect_message: str) -> None:
    headers = logon_root_headers | {"Content-Language": locale}
    r = client.get("/api/getUserInfo", params={"id": 114514}, headers=headers)
    assert r.status_code == 200
    ro = NoneResponse(**r.json())
    assert ro.code == 2
    assert ro.message == expect_message
