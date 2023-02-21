from starlette.testclient import TestClient

from app.main import app
from app.model.response import LoginResponse

client = TestClient(app)


def login(username: str, password: str) -> dict[str, str]:
    login_form = {"grant_type": "password", "username": username, "password": password}
    r = client.post("/api/login", data=login_form)
    assert r.is_success
    ro = LoginResponse(**r.json())
    assert ro.token_type == "bearer"
    token = ro.access_token
    assert token
    return {"Authorization": f"Bearer {token}"}
