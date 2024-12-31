from typing import Any, Literal, TypeVar

import httpx
from httpx._client import USE_CLIENT_DEFAULT, TimeoutTypes, UseClientDefault
from httpx._types import AuthTypes, CookieTypes, HeaderTypes, QueryParamTypes, URLTypes
from pydantic import Json
from starlette.testclient import TestClient

from app.main import app
from app.model.response import LoginResponse, Response

RM = TypeVar("RM")


class CustomTestClient(TestClient):
    def request_with_test(
        self,
        method: Literal["GET", "POST", "DELETE"],
        url: URLTypes,
        response_model: type[RM],
        params: QueryParamTypes | None = None,
        json: Json | None = None,
        headers: HeaderTypes | None = None,
    ) -> RM:
        response = super().request(method, url, params=params, json=json, headers=headers)
        assert response.is_success
        model = Response[response_model](**response.json())
        assert model.code == 0
        return model.data

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
    ) -> httpx.Response:
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


client = CustomTestClient(app)


def login(username: str, password: str) -> dict[str, str]:
    login_form = {"grant_type": "password", "username": username, "password": password}
    r = client.post("/api/login", data=login_form)
    assert r.is_success
    ro = LoginResponse(**r.json())
    assert ro.token_type == "bearer"
    token = ro.access_token
    assert token
    return {"Authorization": f"Bearer {token}"}
