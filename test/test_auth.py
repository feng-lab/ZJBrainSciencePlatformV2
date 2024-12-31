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
