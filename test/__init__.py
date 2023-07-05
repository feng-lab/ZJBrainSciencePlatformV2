from typing import Any

from httpx import Response
from httpx._client import USE_CLIENT_DEFAULT, TimeoutTypes, UseClientDefault
from httpx._types import AuthTypes, CookieTypes, HeaderTypes, QueryParamTypes, URLTypes
from starlette.testclient import TestClient

from app.main import app
from app.model.response import LoginResponse


class CustomDeleteTestClient(TestClient):
    def delete(
        self,
        url: URLTypes,
        *,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | None = None,
        allow_redirects: bool | None = None,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: dict[str, Any] | None = None,
    ) -> Response:
        return super().request(
            "DELETE",
            url,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            allow_redirects=allow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


client = CustomDeleteTestClient(app)


def login(username: str, password: str) -> dict[str, str]:
    login_form = {"grant_type": "password", "username": username, "password": password}
    r = client.post("/api/login", data=login_form)
    assert r.is_success
    ro = LoginResponse(**r.json())
    assert ro.token_type == "bearer"
    token = ro.access_token
    assert token
    return {"Authorization": f"Bearer {token}"}
