from sqlmodel import Field, SQLModel, Column, DateTime, func
from datetime import datetime
from typing import List


class CoreModel(SQLModel):
    created_at: datetime | None = Field(
        default=datetime.now(), nullable=False
    )

    updated_at: datetime | None = Field(
        default_factory=datetime.now, nullable=False
    )
