from datetime import datetime

from pydantic import BaseModel


class Workspace(BaseModel):
    admin_ids: list[str] | None
    color: str
    created: datetime
    domain: str
    id: str
    master_id: str
    name: str
    photo: str
