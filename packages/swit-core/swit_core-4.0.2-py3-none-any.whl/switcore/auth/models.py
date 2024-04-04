from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped

base_model = declarative_base()


class BaseModel(base_model):
    __abstract__ = True

    id: Mapped[int] = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created: Mapped[datetime] = Column(DateTime, default=func.now())
    updated: Mapped[datetime] = Column(DateTime, default=func.now(), onupdate=func.now())


class App(BaseModel):
    __tablename__ = 'app'

    access_token: Mapped[str] = Column(String(500), nullable=False)
    refresh_token: Mapped[str] = Column(String(50), nullable=False)
    iss: Mapped[str] = Column(String(50), nullable=False)
    cmp_id: Mapped[str] = Column(String(50), nullable=False)
    apps_id: Mapped[str] = Column(String(50), nullable=False)


class User(BaseModel):
    __tablename__ = 'user'

    swit_id: Mapped[str] = Column(String(100), nullable=False, index=True)
    access_token: Mapped[str | None] = Column(String(500), nullable=True)
    refresh_token: Mapped[str | None] = Column(String(50), nullable=True)
