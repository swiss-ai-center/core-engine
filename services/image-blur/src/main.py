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
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType

# Imports required by the service's model
import json
import cv2
import numpy as np
from common_code.tasks.service import get_extension

settings = get_settings()


def clamp(val, smallest, largest):
    return max(smallest, min(val, largest))


class MyService(Service):
    """
    Image blur model
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    def __init__(self):
        super().__init__(
            name="Image Blur",
            slug="image-blur",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
                FieldDescription(name="areas", type=[FieldDescriptionType.APPLICATION_JSON]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
            ]
        )

    def process(self, data):
        raw = data["image"].data
        input_type = data["image"].type
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), 1)

        areas = json.loads(data["areas"].data)

        rows = img.shape[0]
        cols = img.shape[1]

        for a in areas:
            a[0] = clamp(int(a[0]), 0, cols)
            a[1] = clamp(int(a[1]), 0, rows)
            a[2] = clamp(int(a[2]), 0, cols)
            a[3] = clamp(int(a[3]), 0, rows)

            x1, x2, y1, y2 = a[0], a[2], a[1], a[3]
            # We need to compute the blur kernel size according to the area size
            areaSize = max(x2 - x1, y2 - y1)
            kernelSize = int(areaSize * 0.08)
            img[y1:y2 + 1, x1:x2 + 1] = cv2.blur(img[y1:y2 + 1, x1:x2 + 1], (kernelSize, kernelSize))
        guessed_extension = get_extension(input_type)
        is_ok, out_buff = cv2.imencode(guessed_extension, img)

        task_data = TaskData(
            data=out_buff.tobytes(),
            type=input_type
        )

        return {
            "result": task_data
        }


api_description = """
This service blurs the image in the given areas.
The areas are given as a list of [x1, y1, x2, y2] coordinates.
"""
api_summary = "Blurs the image in the given areas."

# Define the FastAPI application with information
app = FastAPI(
    title="Image Blur API.",
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
