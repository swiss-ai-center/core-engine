from typing import Optional
from sqlmodel import Field, SQLModel, TypeDecorator, JSON
from datetime import datetime


class CoreModel(SQLModel):
    created_at: Optional[datetime] = Field(default=datetime.now())

    updated_at: Optional[datetime] = Field(default_factory=datetime.now)


class PydanticJSON(TypeDecorator):
    """
    Custom TypeDecorator that automatically dumps Pydantic models
    to JSON-compatible dicts before saving to the DB.
    """
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, list):
            return [
                item.model_dump(mode='json') if hasattr(item, 'model_dump') else item
                for item in value
            ]
        return value
