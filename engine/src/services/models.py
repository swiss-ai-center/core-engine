import re
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel
from pydantic.class_validators import validator
from sqlmodel import Field, SQLModel, Column, JSON, Relationship
from typing import TypedDict
from common.models import CoreModel
from .enums import FieldDescriptionType, ServiceStatus

if TYPE_CHECKING:
    from tasks.models import Task, TaskRead


class FieldDescription(TypedDict):
    """
    Field description
    """
    name: str
    type: List[FieldDescriptionType]


class ServiceBase(CoreModel):
    """
    Base class for Service
    This model is used in subclasses
    """
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    url: str = Field(nullable=False)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    status: ServiceStatus = Field(default=ServiceStatus.AVAILABLE, nullable=False)
    data_in_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)

    @validator("slug")
    def slug_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError("Slug must be in kebab-case format. Example: my-service")
        return v

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class Service(ServiceBase, table=True):
    """
    Service model
    This model is the one that is stored in the database
    """
    __tablename__ = "services"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="service")  # noqa F821


class ServiceRead(ServiceBase):
    """
    Service read model
    This model is used to return a service to the user
    """
    id: UUID


class ServiceReadWithTasks(ServiceRead):
    """
    Service read model with tasks
    This model is used to return a service to the user with the tasks
    """
    tasks: List["TaskRead"]


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
    slug: str | None
    url: str | None
    summary: str | None
    description: str | None
    status: ServiceStatus | None
    data_in_fields: List[FieldDescription] | None
    data_out_fields: List[FieldDescription] | None


class ServiceTaskBase(BaseModel):
    """
    Base class for Service task
    This model is used in subclasses
    """
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_region: str
    s3_host: str
    s3_bucket: str
    task: "TaskRead"
    callback_url: str


class ServiceTask(ServiceTaskBase):
    """
    Service task
    This model is sent to the service with the information
    related to S3 as well as the task to execute
    """
    pass
