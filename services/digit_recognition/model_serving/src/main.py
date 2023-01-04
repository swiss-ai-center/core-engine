import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from config import get_settings
from http_client import HttpClient
from logger import Logger
from service.controller import router as service_router
from service.service import ServiceService
from worker.service import WorkerService
from tasks.controller import router as tasks_router


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
    settings = get_settings()
    logger = Logger(settings)
    logger.set_source(__name__)
    http_client = HttpClient()

    # worker = WorkerService(logger, settings)
    # worker.start()

    service_service = ServiceService(logger, settings, http_client)
    announced = False
    retries = settings.engine_announce_retries
    while not announced and retries > 0:
        announced = await service_service.announce_service()
        retries -= 1
        if not announced:
            time.sleep(settings.engine_announce_retry_delay)
