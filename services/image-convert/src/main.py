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
from PIL import Image

settings = get_settings()


class MyService(Service):
    """
    Image convert model
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    def __init__(self):
        super().__init__(
            name="Image Convert",
            slug="image-convert",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
                FieldDescription(name="format", type=[FieldDescriptionType.TEXT_PLAIN]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
            ]
        )

    def process(self, data):
        # TODO: modify to accept any image format and convert to any image format
        raw = data["image"].data
        input_type = data["image"].type
        output_type = data["format"].data

        if input_type == output_type:
            return {
                "result": TaskData(
                    data=raw,
                    type=output_type,
                )
            }

        if output_type not in MyService.get_output_types():
            raise Exception("Output type not supported.")

        stream = io.BytesIO(raw)
        img = Image.open(stream)
        img = img.convert("RGB")

        out_buff = io.BytesIO()
        img.save(out_buff, format=output_type.split('/')[1])
        out_buff.seek(0)
        return {
            "result": TaskData(
                data=out_buff.read(),
                type=output_type,
            )
        }


api_description = """
This service converts images from different formats to different formats.
Acceptable formats are: image/png, image/jpeg.
"""
api_summary = """
Converts image.
"""

# Define the FastAPI application with information
app = FastAPI(
    title="Image Convert API.",
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
