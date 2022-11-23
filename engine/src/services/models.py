from typing import List
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column, JSON
from common.models import CoreModel


class ServiceBase(CoreModel):
    """
    Base class for Service
    """
    name: str = Field(nullable=False)
    url: str = Field(nullable=False)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    data_in_fields: List[str] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_fields: List[str] | None = Field(sa_column=Column(JSON), default=None, nullable=True)

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class Service(ServiceBase, table=True):
    """
    Service model
    the one that is stored in the database
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class ServiceRead(ServiceBase):
    """
    Service read model
    This model is used to return a service to the user
    """
    id: UUID


class ServiceCreate(ServiceBase):
    """
    Service create model
    This model is used to create a service
    """
    pass


class ServiceUpdate(SQLModel):
    """
    Service update model
    This model is used to update a service
    """
    name: str | None
    url: str | None
    summary: str | None
    description: str | None
    data_in_fields: List[str] | None
    data_out_fields: List[str] | None
