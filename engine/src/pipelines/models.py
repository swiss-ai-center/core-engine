from typing import List
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from execution_units.models import ExecutionUnit
from execution_units.enums import ExecutionUnitStatus
from pipeline_steps.models import PipelineStep, PipelineStepCreate


class Pipeline(ExecutionUnit, table=True):
    """
    Pipeline model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipelines"
    __table_args__ = {"extend_existing": True}

    steps: List[PipelineStep] = Relationship(back_populates="pipeline") # noqa F821
    pipeline_executions: List["PipelineExecution"] = Relationship(back_populates="pipeline") # noqa F821

    __mapper_args__ = {
        "polymorphic_identity": "pipeline",
    }


class PipelineRead(ExecutionUnit):
    """
    Pipeline read model
    This model is used to return a pipeline to the user
    """
    pass


class PipelineReadWithPipelineStepsAndTasks(PipelineRead):
    """
    Pipeline read model with service
    This model is used to return a pipeline to the user with the service
    """
    steps: List[PipelineStep]


class PipelineCreate(ExecutionUnit):
    """
    Pipeline create model
    This model is used to create a pipeline
    """
    steps: List[PipelineStepCreate]


class PipelineUpdate(SQLModel):
    """
    Pipeline update model
    This model is used to update a pipeline
    """
    name: str | None
    summary: str | None
    description: str | None
    status: ExecutionUnitStatus | None
    steps: List[PipelineStepCreate] | None


from pipeline_executions.models import PipelineExecution # noqa E402
Pipeline.update_forward_refs()
