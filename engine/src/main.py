from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_session
from logger import get_logger
from pipelines.controller import router as pipelines_router
from services.controller import router as services_router
from services.service import ServicesService
from stats.controller import router as stats_router
from tasks.controller import router as tasks_router
from tasks.service import TasksService
from storage.controller import router as storage_router
from storage.service import StorageService
from config import get_settings, Environment
from database import initialize_db
from timer import Timer
from http_client import HttpClient


timers = []
settings = get_settings()

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
    # TODO: Add license information
    # license_info={
    #     "name": "",
    #     "url": "",
    # },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from other files
app.include_router(pipelines_router, tags=['Pipelines'])
app.include_router(services_router, tags=['Services'])
app.include_router(stats_router, tags=['Stats'])
app.include_router(tasks_router, tags=['Tasks'])

# For developing purposes only
if (settings.environment == Environment.DEVELOPMENT):
    app.include_router(storage_router, tags=['Storage'])


# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)


@app.on_event("startup")
async def startup_event():
    # Manual instances because startup events doesn't support Dependency Injection
    # https://github.com/tiangolo/fastapi/issues/2057
    # https://github.com/tiangolo/fastapi/issues/425
    engine = initialize_db(settings)
    session_generator = get_session(engine)
    session = next(session_generator)
    http_client = HttpClient()

    storage_service = StorageService(get_logger(settings), settings)
    tasks_service = TasksService(get_logger(settings), session)
    services_service = ServicesService(get_logger(settings), storage_service, tasks_service, settings, session, http_client)

    # Check storage
    await storage_service.check_storage_availability()

    # Instantiate services in database
    await services_service.check_services_availability(app)

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
