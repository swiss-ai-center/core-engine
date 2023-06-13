from database import get_session
from common_code.logger.logger import get_logger
from tasks.service import TasksService
from services.service import ServicesService
from pipeline_executions.service import PipelineExecutionsService
from storage.service import StorageService
from config import get_settings
from database import initialize_db
from http_client import HttpClient


def test_services_service():
    settings = get_settings()
    engine = initialize_db(settings=settings)
    session_generator = get_session(engine)
    session = next(session_generator)
    http_client = HttpClient()

    storage_service = StorageService(
        logger=get_logger(settings),
        settings=settings,
    )
    pipeline_executions_service = PipelineExecutionsService(
        logger=get_logger(settings),
        session=session,
    )
    tasks_service = TasksService(
        logger=get_logger(settings),
        session=session,
        http_client=http_client,
        pipeline_executions_service=pipeline_executions_service,
        settings=settings,
        storage_service=storage_service,
    )
    services_service = ServicesService(
        logger=get_logger(settings),
        storage_service=storage_service,
        tasks_service=tasks_service,
        settings=settings,
        session=session,
        http_client=http_client,
    )

    print(services_service)
