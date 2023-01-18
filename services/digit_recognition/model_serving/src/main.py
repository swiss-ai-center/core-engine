import asyncio
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from config import get_settings
from http_client import HttpClient
from logger.logger import get_logger
from service.controller import router as service_router
from service.service import ServiceService
from storage.service import StorageService
from tasks.controller import router as tasks_router
from tasks.service import TasksService

tasks_service: TasksService | None = None
api_description = """
Recognizes a digit in an image using mnist trained model
"""

# Define the FastAPI application with information
app = FastAPI(
    title="Digit Recognition API.",
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

# Include routers from other files
app.include_router(service_router, tags=['Service'])
app.include_router(tasks_router, tags=['Tasks'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)


@app.on_event("startup")
async def startup_event():
    global tasks_service
    settings = get_settings()
    logger = get_logger(settings)
    http_client = HttpClient()
    storage_service = StorageService(logger)
    tasks_service = TasksService(logger, settings, http_client, storage_service)
    service_service = ServiceService(logger, settings, http_client)

    # Start the tasks service
    tasks_service.start()

    async def announce():
        # TODO: enhance this to allow multiple engines to be used
        announced = False
        retries = settings.engine_announce_retries
        while not announced and retries > 0:
            announced = await service_service.announce_service()
            retries -= 1
            if not announced:
                time.sleep(settings.engine_announce_retry_delay)
                if retries == 0:
                    logger.warning(f"Aborting service announcement after {settings.engine_announce_retries} retries")

    # Announce the service to its engine
    asyncio.ensure_future(announce())


@app.on_event("shutdown")
async def shutdown_event():
    global tasks_service
    await tasks_service.stop()
