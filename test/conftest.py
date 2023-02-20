import pytest
from fastapi.testclient import TestClient

from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.main import app
from app.model.response import LoginResponse

client = TestClient(app)


@pytest.fixture(scope="session")
def logon_root_headers() -> dict[str, str]:
    login_form = {"grant_type": "password", "username": ROOT_USERNAME, "password": ROOT_PASSWORD}
    r = client.post("/api/login", data=login_form)
    assert r.is_success
    ro = LoginResponse(**r.json())
    assert ro.token_type == "bearer"
    token = ro.access_token
    assert token
    return {"Authorization": f"Bearer {token}"}
