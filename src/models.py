from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Users(SQLModel, table=True):

    __tablename__ = "users"

    id:Optional[int] = Field(default=None, primary_key=True)
    username:str = Field(nullable=False, unique=True)
    password:str = Field(nullable=False)
    email:str = Field(nullable=False, unique=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    role_id: int = Field(default=2 ,foreign_key='roles.id', nullable=False)

class Roles(SQLModel, table=True):

    __tablename__ = "roles"

    id:Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)