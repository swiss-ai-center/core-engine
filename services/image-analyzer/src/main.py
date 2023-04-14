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
from common_code.service.models import Service, FieldDescription
from common_code.service.enums import ServiceStatus, FieldDescriptionType

# Imports required by the service's model
import io
import json
from PIL import Image
from PIL.ExifTags import TAGS

settings = get_settings()


class MyService(Service):
    """
    Image analyzer model
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    def __init__(self):
        super().__init__(
            name="Image Analyzer",
            slug="image-analyzer",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.APPLICATION_JSON]),
            ]
        )

    def process(self, data):
        raw = data["image"].data
        stream = io.BytesIO(raw)
        img = Image.open(stream)
        metadata = {"Format": img.get_format_mimetype()}

        exif = img.getexif()
        for tagId, val in exif.items():
            name = TAGS[tagId] if tagId in TAGS else "0x{tagId:x}".format(tagId=tagId)
            metadata[name] = val if type(val) in [str, int, float, bool] else str(val)

        return {
            "result": TaskData(
                data=json.dumps(metadata),
                type=FieldDescriptionType.APPLICATION_JSON
            )
        }


api_description = """
This service analyzes images. It returns the following information:
- Format (e.g. image/jpeg)
- Image width (e.g. 1920)
- Image length (e.g. 1080)
- Bits per sample (e.g. (8, 8, 8))
- Photometric interpretation (e.g. 2)
- Resolution unit (e.g. 3)
- Exif offset (e.g. 236)
- Software (e.g. Adobe Photoshop CC 2017 (Macintosh))
- Orientation (e.g. 1)
- Date time (e.g. 2017:05:02 16:00:48)
- Samples per pixel (e.g. 3)
- X resolution (e.g. 118.1102)
- Y resolution (e.g. 118.1102)
"""
api_summary = """
Analyze images. Return information about the image
"""

# Define the FastAPI application with information
app = FastAPI(
    title="Image Analyzer API.",
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
        # TODO: enhance this to allow multiple engines to be used
        announced = False

        retries = settings.engine_announce_retries
        while not announced and retries > 0:
            announced = await service_service.announce_service(my_service)
            retries -= 1
            if not announced:
                time.sleep(settings.engine_announce_retry_delay)
                if retries == 0:
                    logger.warning(f"Aborting service announcement after {settings.engine_announce_retries} retries")

    # Announce the service to its engine
    asyncio.ensure_future(announce())


@app.on_event("shutdown")
async def shutdown_event():
    # Global variable
    global service_service
    my_service = MyService()
    await service_service.graceful_shutdown(my_service)
