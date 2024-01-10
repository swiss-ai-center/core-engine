from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, AnyHttpUrl
from sqlmodel import SQLModel, Relationship, Field, Column, JSON, String
from common_code.common.models import FieldDescription, ExecutionUnitTag
from execution_units.enums import ExecutionUnitStatus
from execution_units.models import ExecutionUnitBase


class ServiceBase(ExecutionUnitBase):
    """
    Base class for a Service
    This model is used in subclasses
    """
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    status: ExecutionUnitStatus = Field(
        default=ExecutionUnitStatus.AVAILABLE, nullable=False
    )
    data_in_fields: List[FieldDescription] | None = Field(
        sa_column=Column(JSON), default=None
    )
    data_out_fields: List[FieldDescription] | None = Field(
        sa_column=Column(JSON), default=None
    )
    tags: List[ExecutionUnitTag] | None = Field(sa_column=Column(JSON), default=None)
    url: AnyHttpUrl = Field(sa_column=Column(String))
    has_ai: bool | None = Field(default=False, nullable=True)

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
    tasks: List["Task"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"}, back_populates="service"
    )  # noqa F821
    pipeline_steps: List["PipelineStep"] = Relationship(
        back_populates="service"
    )  # noqa F821


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

    tasks: "List[TaskRead]"


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
    url: AnyHttpUrl | None
    summary: str | None
    description: str | None
    status: ExecutionUnitStatus | None
    data_in_fields: List[FieldDescription]
    data_out_fields: List[FieldDescription]
    tags: List[ExecutionUnitTag] | None
    has_ai: bool | None


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
    callback_url: AnyHttpUrl


class ServiceTask(ServiceTaskBase):
    """
    Service task
    This model is sent to the service with the information
    related to S3 as well as the task to execute
    """

    pass


class ServicesWithCount(BaseModel):
    """
    Services with count
    This model is used to return a list of filtered services with the count of all services matching a filter
    """

    count: int
    services: List[ServiceRead]


from tasks.models import Task, TaskRead  # noqa E402

Service.update_forward_refs()
ServiceTask.update_forward_refs()
ServiceTaskBase.update_forward_refs()
ServiceReadWithTasks.update_forward_refs()
