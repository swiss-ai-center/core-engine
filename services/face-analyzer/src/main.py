import asyncio
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from common_code.config import get_settings
from pydantic import Field
from common_code.http_client import HttpClient
from common_code.logger.logger import get_logger
from common_code.service.controller import router as service_router
from common_code.service.service import ServiceService
from common_code.storage.service import StorageService
from common_code.tasks.controller import router as tasks_router
from common_code.tasks.service import TasksService
from common_code.tasks.models import TaskData
from common_code.service.models import Service
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from common_code.common.models import FieldDescription, ExecutionUnitTag

# Imports required by the service's model
import io
import json
from PIL import Image
from deepface import DeepFace
import numpy as np

settings = get_settings()


class MyService(Service):
    """
    Face analyzer service model
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    def __init__(self):
        super().__init__(
            name="Face Analyzer",
            slug="face-analyzer",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.APPLICATION_JSON]),
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.IMAGE_RECOGNITION,
                    acronym=ExecutionUnitTagAcronym.IMAGE_RECOGNITION
                ),
            ],
            has_ai=True
        )

    def process(self, data):
        # Get raw image data
        raw = data["image"].data
        buff = io.BytesIO(raw)
        img_pil = Image.open(buff)
        img = np.array(img_pil)
        diagnos = DeepFace.analyze(
            img_path=img,
            actions=['age', 'gender', 'race', 'emotion'],
            enforce_detection=True,
            detector_backend="retinaface",
        )

        return {
            "result": TaskData(
                data=json.dumps(diagnos),
                type=FieldDescriptionType.APPLICATION_JSON
            )
        }


api_description = """
Analyse faces in images. Returns a JSON object with the following fields:
- age (Age of the person in the image),
- region (Region of the person in the image),
- gender (Gender of the person in the image),
- race (Race of the person in the image),
- dominant_race (Dominant race of the person in the image),
- emotion (Emotion of the person in the image),
- dominant_emotion (The dominant emotion of the person in the image)
"""
api_summary = """
Analyzes the faces in images.
"""

# Define the FastAPI application with information
app = FastAPI(
    title="Face Analyzer API.",
    description=api_description,
    version="1.0.0",
    contact={
        "name": "Swiss AI Center",
        "url": "https://swiss-ai-center.ch/",
        "email": "ia.recherche@hes-so.ch",
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


service_service: ServiceService | None = None


@app.on_event("startup")
async def startup_event():
    # Manual instances because startup events doesn't support Dependency Injection
    # https://github.com/tiangolo/fastapi/issues/2057
    # https://github.com/tiangolo/fastapi/issues/425

    # Global variable
    global service_service

    logger = get_logger(settings)
    http_client = HttpClient()
    storage_service = StorageService(logger)
    my_service = MyService()
    tasks_service = TasksService(logger, settings, http_client, storage_service)
    service_service = ServiceService(logger, settings, http_client, tasks_service)

    tasks_service.set_service(my_service)

    # Start the tasks service
    tasks_service.start()

    async def announce():
        retries = settings.engine_announce_retries
        for engine_url in settings.engine_urls:
            announced = False
            while not announced and retries > 0:
                announced = await service_service.announce_service(my_service, engine_url)
                retries -= 1
                if not announced:
                    time.sleep(settings.engine_announce_retry_delay)
                    if retries == 0:
                        logger.warning(f"Aborting service announcement after "
                                       f"{settings.engine_announce_retries} retries")

    # Announce the service to its engine
    asyncio.ensure_future(announce())


@app.on_event("shutdown")
async def shutdown_event():
    # Global variable
    global service_service
    my_service = MyService()
    for engine_url in settings.engine_urls:
        await service_service.graceful_shutdown(my_service, engine_url)
