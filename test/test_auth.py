from test import client
from app.common.config import config
import pytest

from app.api import encrypt_password
from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.model.response import NoneResponse

@pytest.mark.skipif(config.ENABLE_KEYCLOAK, reason="当前模式不支持登出")
@pytest.mark.parametrize(
    "username,password",
    [("not exists user", encrypt_password("some password")), (ROOT_USERNAME, encrypt_password("wrong password"))],
)
def test_login_wrong_username_or_password(username: str, password: str):
    login_form = {"grant_type": "password", "username": "not exists user", "password": encrypt_password(ROOT_PASSWORD)}
    r = client.post("/api/login", data=login_form)
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 3

@pytest.mark.skipif(config.ENABLE_KEYCLOAK, reason="当前模式不支持登出")
def test_logout(logon_root_headers: dict[str, str]):
    r = client.post("/api/logout", headers=logon_root_headers)
 # 调试信息
    assert r.is_success, f"登出失败，状态码: {r.status_code}"
    ro = NoneResponse(**r.json())
    assert ro.code == 0

@pytest.mark.skipif(config.ENABLE_KEYCLOAK, reason="当前模式不支持登出")
def test_logout_unauthorized():
    r = client.post("/api/logout")
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 3


@pytest.mark.skipif(not config.ENABLE_KEYCLOAK, reason="当前模式不支持登出")
@pytest.mark.parametrize(
    "username,password",
    [("not_exists_user", "some_password"), ("valid_user", "wrong_password")],
)
def test_login_wrong_username_or_password(username: str, password: str):

    login_form = {"grant_type": "password", "username": username, "password": password}
    response = client.post("/api/login_keycloak", data=login_form)
    print(response.status_code)
    # 检查登录失败的情况
    assert response.status_code == 500, "Expected 401 for invalid credentials"

    ro = NoneResponse(**response.json())
    assert ro.code == 1

@pytest.mark.skipif(not config.ENABLE_KEYCLOAK, reason="当前模式不支持登出")
def test_logout_unauthorized():
    r = client.post("/api/logout_keycloak")
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 3