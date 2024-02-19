from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class CoreModel(SQLModel):
    created_at: Optional[datetime] = Field(default=datetime.now())

    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
