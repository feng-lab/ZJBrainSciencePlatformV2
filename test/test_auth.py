from test import client

import pytest

from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.model.response import NoneResponse


@pytest.mark.parametrize(
    "username,password", [("not exists user", "some password"), (ROOT_USERNAME, "wrong password")]
)
def test_login_wrong_username_or_password(username: str, password: str):
    login_form = {
        "grant_type": "password",
        "username": "not exists user",
        "password": ROOT_PASSWORD,
    }
    r = client.post("/api/login", data=login_form)
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 1


def test_logout(logon_root_headers: dict[str, str]):
    r = client.post("/api/logout", headers=logon_root_headers)
    assert r.is_success
    ro = NoneResponse(**r.json())
    assert ro.code == 0


def test_logout_unauthorized():
    r = client.post("/api/logout")
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 1
