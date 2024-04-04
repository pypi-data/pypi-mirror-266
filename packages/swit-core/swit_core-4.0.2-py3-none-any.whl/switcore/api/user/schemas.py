from pydantic import BaseModel


class SwitUser(BaseModel):
    cmp_id: str
    color: str | None = None
    department: str | None = None
    id: str
    language: str
    name: str
    photo: str | None = None
    status: int | None = None
    status_msg: str | None = None
    tel: str | None = None
    timezone: str | None = None
    user_email: str | None = None
