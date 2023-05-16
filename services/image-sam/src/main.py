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
from common_code.tasks.service import TasksService, get_extension
from common_code.tasks.models import TaskData
from common_code.service.models import Service
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from common_code.common.models import FieldDescription, ExecutionUnitTag

# Imports required by the service's model
import cv2
import numpy as np
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

settings = get_settings()
# We set the seed to get the same colors for the classes
np.random.seed(42)


class MyService(Service):
    """
    Image Segment Anything Model (SAM)
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    def __init__(self):
        super().__init__(
            name="Image Segment Anything Model (SAM)",
            slug="image-sam",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(
                    name="image",
                    type=[
                        FieldDescriptionType.IMAGE_PNG,
                        FieldDescriptionType.IMAGE_JPEG,
                    ],
                ),
            ],
            data_out_fields=[
                FieldDescription(
                    name="result",
                    type=[
                        FieldDescriptionType.IMAGE_PNG,
                        FieldDescriptionType.IMAGE_JPEG,
                    ],
                ),
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.IMAGE_RECOGNITION,
                    acronym=ExecutionUnitTagAcronym.IMAGE_RECOGNITION,
                ),
            ],
        )
        sam = sam_model_registry["vit_b"](checkpoint="../model/sam_vit_b_01ec64.pth")
        self.model = SamAutomaticMaskGenerator(sam)

    def show_anns(self, anns, img):
        if len(anns) == 0:
            return

        sorted_anns = sorted(anns, key=(lambda x: x["area"]), reverse=True)
        img_h, img_w = img.shape[:2]
        overlay = np.zeros((img_h, img_w, 3), dtype=np.uint8)

        for ann in sorted_anns:
            m = ann["segmentation"]
            color_mask = np.random.random((1, 3)) * 255
            color_mask = np.array(color_mask, dtype=np.uint8)
            mask = np.zeros((img_h, img_w, 3), dtype=np.uint8)
            mask[:, :, 0] = color_mask[0][0]
            mask[:, :, 1] = color_mask[0][1]
            mask[:, :, 2] = color_mask[0][2]
            mask = mask * (m[:, :, np.newaxis])
            overlay = cv2.addWeighted(overlay, 1, mask, 0.5, 0)

        output_img = cv2.addWeighted(img, 0.6, overlay, 0.5, 0)
        return output_img

    def process(self, data):
        raw = data["image"].data
        input_type = data["image"].type
        img_np = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

        masks = self.model.generate(img_np)
        img_masked = self.show_anns(masks, img_np)

        guessed_extension = get_extension(input_type)
        _, out_buff = cv2.imencode(guessed_extension, img_masked)
        return {"result": TaskData(data=out_buff.tobytes(), type=input_type)}


api_description = """
This service segments an image.
"""
api_summary = """
Segments anything in an image.
"""

# Define the FastAPI application with information
app = FastAPI(
    title="Image Segment Anything API.",
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
app.include_router(service_router, tags=["Service"])
app.include_router(tasks_router, tags=["Tasks"])

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
