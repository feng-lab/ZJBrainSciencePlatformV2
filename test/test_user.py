from datetime import datetime
from test import client, login
from typing import Any

import pytest

from app.model.response import NoneResponse, Page, Response
from app.model.schema import UserResponse


@pytest.fixture(scope="module")
def created_user(logon_root_headers) -> dict[str, Any]:
    create_user = {
        "username": "test_username",
        "staff_id": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "password": "test_user_password",
        "access_level": 10,
    }
    r = client.post("/api/createUser", headers=logon_root_headers, json=create_user)
    assert r.is_success
    ro = Response[int](**r.json())
    assert ro.code == 0
    assert ro.data > 0
    create_user["id"] = ro.data
    create_user["headers"] = login(create_user["staff_id"], create_user["password"])

    yield create_user

    delete_user = {"id": create_user["id"]}
    r = client.request("DELETE", "/api/deleteUser", headers=logon_root_headers, json=delete_user)
    assert r.is_success
    ro = NoneResponse(**r.json())
    assert ro.code == 0


def test_get_current_user_info(created_user: dict[str, Any]):
    r = client.get("/api/getCurrentUserInfo", headers=created_user["headers"])
    assert r.is_success
    ro = Response[UserResponse](**r.json())
    assert ro.code == 0
    assert ro.data.username == created_user["username"]
    assert ro.data.staff_id == created_user["staff_id"]


def test_get_user_info(created_user: dict[str, Any], logon_root_headers: dict[str, str]):
    params = {"id": created_user["id"]}
    r = client.get("/api/getUserInfo", headers=logon_root_headers, params=params)
    assert r.is_success
    ro = Response[UserResponse](**r.json())
    assert ro.code == 0
    assert ro.data.username == created_user["username"]
    assert ro.data.staff_id == created_user["staff_id"]


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"username": "ro"},
        {"staff_id": "root"},
        {"access_level": "1000"},
        {"offset": "0", "limit": "1", "include_deleted": "false"},
    ],
)
def test_get_users_by_page(params: dict[str, str], logon_root_headers: dict[str, str]):
    r = client.get("/api/getUsersByPage", headers=logon_root_headers, params=params)
    assert r.is_success
    ro = Response[Page[UserResponse]](**r.json())
    assert ro.code == 0
    assert ro.data.total > 0 and len(ro.data.items) > 0
    assert "root" in [user.staff_id for user in ro.data.items]


def test_update_access_level(created_user: dict[str, Any], logon_root_headers: dict[str, str]):
    new_access_level = 7
    body = {"id": created_user["id"], "access_level": new_access_level}
    r = client.post("/api/updateUserAccessLevel", headers=logon_root_headers, json=body)
    assert r.is_success
    ro = NoneResponse(**r.json())
    assert ro.code == 0

    r = client.get(f"/api/getUserInfo?id={created_user['id']}", headers=logon_root_headers)
    assert r.is_success
    ro = Response[UserResponse](**r.json())
    assert ro.code == 0
    assert ro.data.access_level == new_access_level


def test_update_password(created_user: dict[str, Any], logon_root_headers: dict[str, str]):
    new_password = "new password"
    body = {"old_password": created_user["password"], "new_password": new_password}
    r = client.post("/api/updatePassword", headers=created_user["headers"], json=body)
    assert r.is_success
    ro = NoneResponse(**r.json())
    assert ro.code == 0

    login_form = {
        "grant_type": "password",
        "username": created_user["staff_id"],
        "password": created_user["password"],
    }
    r = client.post("/api/login", data=login_form)
    assert r.status_code == 401
    ro = NoneResponse(**r.json())
    assert ro.code == 1

    login(created_user["staff_id"], new_password)
