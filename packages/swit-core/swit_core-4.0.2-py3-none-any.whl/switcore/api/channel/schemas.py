from datetime import datetime

from pydantic import BaseModel


class Channel(BaseModel):
    created: datetime
    description: str
    host_id: str
    id: str
    is_archived: bool
    is_member: bool
    is_prev_chat_visible: bool
    is_private: bool
    is_starred: bool
    name: str
    type: str
