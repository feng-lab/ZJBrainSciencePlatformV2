from test import client
from app.common.config import config
import pytest

from app.api import encrypt_password
from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.model.response import NoneResponse

@pytest.mark.skipif(config.ENABLE_KEYCLOAK, reason="跳过测试，因为 key_cloak 为 True")
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

@pytest.mark.skipif(config.ENABLE_KEYCLOAK, reason="跳过测试，因为 key_cloak 为 True")
def test_logout(logon_root_headers: dict[str, str]):
    r = client.post("/api/logout", headers=logon_root_headers)
    assert r.is_success
    ro = NoneResponse(**r.json())
    assert ro.code == 0

@pytest.mark.skipif(config.ENABLE_KEYCLOAK, reason="跳过测试，因为 key_cloak 为 True")
def test_logout_unauthorized():
    r = client.post("/api/logout")
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 3

KEYCLOAK_USERNAME = "keycloak_user"
KEYCLOAK_PASSWORD = "keycloak_password"

@pytest.mark.skipif(not config.ENABLE_KEYCLOAK, reason="跳过测试，因为 key_cloak 为 False")
@pytest.mark.parametrize(
    "username,password",
    [("not exists user", "some password"), ("keycloak_user", "wrong password")],
)
def test_keycloak_login_wrong_username_or_password(username: str, password: str):
    """
    测试 Keycloak 登录接口，验证错误的用户名或密码是否返回 401 状态码。
    """
    login_form = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }
    r = client.post("/api/login_keycloak", data=login_form)
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 3

@pytest.mark.skipif(not config.ENABLE_KEYCLOAK, reason="跳过测试，因为 keycloak 为 False")
def test_keycloak_logout(logon_keycloak_headers: dict[str, str]):
    """
    测试 Keycloak 登出接口，验证成功登出是否返回 200 状态码。
    """
    r = client.post("/api/login_keycloak", headers=logon_keycloak_headers)
    assert r.status_code == 200
    ro = NoneResponse(**r.json())
    assert ro.code == 0  # 假设成功码为 0

@pytest.mark.skipif(not config.ENABLE_KEYCLOAK, reason="跳过测试，因为 keycloak 为 False")
def test_keycloak_logout_unauthorized():
    """
    测试 Keycloak 登出接口，验证未授权用户是否返回 401 状态码。
    """
    r = client.post("/api/keycloak/logout")
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 3
