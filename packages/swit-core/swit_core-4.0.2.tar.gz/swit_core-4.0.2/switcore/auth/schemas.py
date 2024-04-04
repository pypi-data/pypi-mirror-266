from pydantic import BaseModel, ConfigDict


class SwitToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    token_type: str
    scope: str


class Payload(BaseModel):
    aud: str
    exp: int
    iss: str
    sub: str
    cmp_id: str | None = None
    apps_id: str
    app_user_id: str
    issue_type: int


class UserSchema(BaseModel):
    swit_id: str
    access_token: str
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)
