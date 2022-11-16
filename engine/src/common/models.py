from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import List


class CoreModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class APIDescription(SQLModel):
    route: str
    summary: str | None
    description: str | None
    body: str | dict | List[str]
    bodyType: str | List[str] | None
    resultType: str | None
