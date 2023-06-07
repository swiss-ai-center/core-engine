import copy
import io
import os
import pytest
from botocore.exceptions import ClientError
from common_code.logger.logger import get_logger
from fastapi import UploadFile
from common.exceptions import NotFoundException, InternalServerErrorException
from pipeline_executions.models import PipelineExecution
from pipeline_executions.service import PipelineExecutionsService
from storage.service import StorageService
from config import get_settings
from uuid import UUID
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="pipeline_executions_service")
def pipeline_executions_service_fixture(session: Session):
    settings = get_settings()

    pipeline_executions_service = PipelineExecutionsService(logger=get_logger(settings), session=session)

    yield pipeline_executions_service


def test_pipeline_executions_service_create(pipeline_executions_service: PipelineExecutionsService):
    pipeline_execution = PipelineExecution()
    await pipeline_executions_service.create(pipeline_execution)
