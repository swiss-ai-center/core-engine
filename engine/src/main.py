from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import initialize_db, get_session
from logger import Logger
from pipelines.controller import router as pipelines_router
from services.controller import router as services_router
from services.service import ServicesService
from stats.controller import router as stats_router
from tasks.controller import router as tasks_router
from timer import Timer

timers = []

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

# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)

@app.on_event("startup")
async def startup_event():
    # Manual instances because startup events doesn't support Dependency Injection
    settings = get_settings()
    engine = initialize_db(settings)
    session = get_session(engine)
    logger = Logger()
    services_service = ServicesService(logger, None, *session)
    # Instantiate services in database
    services_service.instantiate_services(app)
    # TODO: Add storage service
    tick = 30

    # Check for services that are not running
    checkServicesTimer = Timer(
        timeout=tick,
        callback=services_service.check_services_availability,
        app_ref=app)
    checkServicesTimer.start()
    timers.append(checkServicesTimer)

@app.on_event("shutdown")
async def shutdown_event():
    for timer in timers:
        timer.stop()

