from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from connection_manager.connection_manager import ConnectionManager, get_connection_manager
from connection_manager.models import ConnectionData, Message, MessageType, MessageSubject
from database import get_session
from common_code.logger.logger import get_logger
from pipelines.controller import router as pipelines_router
from pipeline_executions.controller import router as pipeline_executions_router
from services.controller import router as services_router
from stats.controller import router as stats_router
from tasks.controller import router as tasks_router
from storage.controller import router as storage_router
from tasks.service import TasksService
from services.service import ServicesService
from pipelines.service import PipelinesService
from pipeline_executions.service import PipelineExecutionsService
from storage.service import StorageService
from config import get_settings
from database import initialize_db
from timer import Timer
from http_client import HttpClient

timers = []
connection_manager: ConnectionManager = get_connection_manager()


api_description = """
CSIA-PME API - The **best** API in the world.
"""

# Define the FastAPI application with information
app = FastAPI(
    title="CSIA-PME API",
    description=api_description,
    version="0.0.1",
    contact={
        "name": "CSIA-PME",
        "url": "https://swiss-ai-center.ch/",
        "email": "info@swiss-ai-center.ch",
    },
    swagger_ui_parameters={
        "tagsSorter": "alpha",
        "operationsSorter": "method",
    },
    license_info={
        "name": "GNU Affero General Public License v3.0 (GNU AGPLv3)",
        "url": "https://choosealicense.com/licenses/agpl-3.0/",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from other files
app.include_router(pipeline_executions_router, tags=['Pipeline Executions'])
app.include_router(pipelines_router, tags=['Pipelines'])
app.include_router(services_router, tags=['Services'])
app.include_router(stats_router, tags=['Stats'])
app.include_router(storage_router, tags=['Storage'])
app.include_router(tasks_router, tags=['Tasks'])


# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global connection_manager
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            connection = connection_manager.set_linked_id(websocket, data["linked_id"])
            connection = connection_manager.set_execution_type(websocket, data["execution_type"])
            connection_data = ConnectionData(linked_id=connection.linked_id, execution_type=connection.execution_type)
            message = Message(
                message={
                    "text": "Connection linked",
                    "data": connection_data.dict(),
                },
                type=MessageType.SUCCESS, subject=MessageSubject.CONNECTION
            )
            await connection_manager.send_json(message, connection.linked_id)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast("Client disconnected")


@app.on_event("startup")
async def startup_event():
    global connection_manager
    # Manual instances because startup events doesn't support Dependency Injection
    # https://github.com/tiangolo/fastapi/issues/2057
    # https://github.com/tiangolo/fastapi/issues/425
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
        connection_manager=connection_manager,
    )
    services_service = ServicesService(
        logger=get_logger(settings),
        storage_service=storage_service,
        tasks_service=tasks_service,
        settings=settings,
        session=session,
        http_client=http_client,
    )
    pipelines_service = PipelinesService(
        logger=get_logger(settings),
        storage_service=storage_service,
        session=session,
        pipeline_executions_service=pipeline_executions_service,
        tasks_service=tasks_service,
        settings=settings,
        services_service=services_service,
        http_client=http_client,
    )

    # Check storage
    await storage_service.check_storage_availability()

    # Instantiate services in database
    await services_service.check_services_availability(app)

    # Enable pipelines
    pipelines_service.enable_pipelines(app)

    # Check for services that are not running
    check_services_timer = Timer(
        timeout=settings.check_services_availability_interval,
        callback=services_service.check_services_availability,
        app=app,
    )

    check_services_timer.start()

    timers.append(check_services_timer)


@app.on_event("shutdown")
async def shutdown_event():
    for timer in timers:
        timer.stop()
