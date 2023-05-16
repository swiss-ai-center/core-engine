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
import tensorflow as tf
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import io

settings = get_settings()


class MyService(Service):
    """
    Autoencoder Anomaly detection
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    def __init__(self):
        super().__init__(
            name="Autoencoder anomaly detection",
            slug="ae-anomaly-detection",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(name="text", type=[FieldDescriptionType.TEXT_CSV, FieldDescriptionType.TEXT_PLAIN]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.IMAGE_PNG]),
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.ANOMALY_DETECTION,
                    acronym=ExecutionUnitTagAcronym.ANOMALY_DETECTION
                ),
            ]
        )
        self.model = tf.keras.models.load_model("../ae_model.h5")

    def process(self, data):
        raw = str(data["text"].data)[2:-1]
        raw = raw.replace('\\t', ',').replace('\\n', '\n').replace('\\r', '\n')
        X_test = pd.read_csv(io.StringIO(raw), dtype={"value": np.float64})

        # Use the model to reconstruct the original time series data
        reconstructed_X = self.model.predict(X_test)

        # Calculate the reconstruction error for each point in the time series
        reconstruction_error = np.square(X_test - reconstructed_X).mean(axis=1)

        err = X_test
        fig, ax = plt.subplots(figsize=(20, 6))

        a = err.loc[reconstruction_error >= np.max(reconstruction_error)]  # anomaly

        ax.plot(err, color='blue', label='Normal')

        ax.scatter(a.index, a, color='red', label='Anomaly')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # NOTE that the result must be a dictionary with the keys being the field names set in the data_out_fields
        return {
            "result": TaskData(data=buf.read(), type=FieldDescriptionType.IMAGE_PNG)
        }


api_description = """
Anomaly detection of a time series with an autoencoder
"""
api_summary = """
Anomaly detection of a time series with an autoencoder
"""

# Define the FastAPI application with information
app = FastAPI(
    title="Autoencoder Anomaly Detection",
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
        retries = settings.engine_announce_retries
        for engine_url in settings.engine_url:
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
    for engine_url in settings.engine_url:
        await service_service.graceful_shutdown(my_service, engine_url)
