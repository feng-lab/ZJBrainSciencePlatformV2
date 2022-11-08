from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    account: str = Field(title="用户名")
    password: str = Field(title="用户密码")
