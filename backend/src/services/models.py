from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, AnyHttpUrl
from sqlmodel import SQLModel, Relationship, Field, Column, JSON, String
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common.models import CoreModel
from execution_units.enums import ExecutionUnitStatus
from pydantic_settings import SettingsConfigDict


class ServiceBase(CoreModel):
    """
    Base class for a Service
    This model is used in subclasses
    """
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

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

    name: str | None = None
    slug: str | None = None
    url: AnyHttpUrl | None = None
    summary: str | None = None
    description: str | None = None
    status: ExecutionUnitStatus | None = None
    data_in_fields: List[FieldDescription] | None = None
    data_out_fields: List[FieldDescription] | None = None
    tags: List[ExecutionUnitTag] | None = None
    has_ai: bool | None = None


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


from pipeline_steps.models import PipelineStep  # noqa E402
from tasks.models import Task, TaskRead  # noqa E402

Service.model_rebuild()
ServiceTask.model_rebuild()
ServiceTaskBase.model_rebuild()
ServiceReadWithTasks.model_rebuild()
