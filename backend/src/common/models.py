from sqlmodel import Field, SQLModel
from datetime import datetime


class CoreModel(SQLModel):
    created_at: datetime | None = Field(
        default=datetime.now(), nullable=False
    )

    updated_at: datetime | None = Field(
        default_factory=datetime.now, nullable=False
    )
