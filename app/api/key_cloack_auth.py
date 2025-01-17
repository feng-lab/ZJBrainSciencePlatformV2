from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from keycloak.exceptions import KeycloakAuthenticationError

from app.api import wrap_api_response
from app.common.context import LogoutALLContest
from app.common.keycloak_user_auth import keycloak_openid
from app.model.response import LoginResponse, NoneResponse

router = APIRouter(tags=["auth"])


@router.post("/api/login_keycloak", description="用户登录，获取AccessToken", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    try:
        token = keycloak_openid.token(form.username, form.password)
        access_token = token["access_token"]
        # refresh_token = token["refresh_token"]
        return LoginResponse(access_token=access_token, token_type="bearer")
    except KeycloakAuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/api/logout_keycloak", description="用户登出", response_model=NoneResponse)
@wrap_api_response
def logout(ctx: LogoutALLContest = Depends()) -> None:
    try:
        # ex_token = keycloak_openid.exchange_token(
        #     token=ctx.token,  # ctx.token 是你现有的 access_token
        #     subject_token_type="urn:ietf:params:oauth:token-type:access_token",  #
        #     requested_token_type="urn:ietf:params:oauth:token-type:refresh_token", # 请求一个新的 refresh_token
        # )
        # print(ex_token)
        keycloak_openid.logout(ctx.token)
        return {"message": "Logged out successfully"}

    except Exception as e:

        raise HTTPException(status_code=500, detail="Failed to logout from Keycloak")
