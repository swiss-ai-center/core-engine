import asyncio
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from config import get_settings
from pydantic import Field
from http_client import HttpClient
from logger.logger import get_logger
from service.controller import router as service_router
from service.service import ServiceService
from storage.service import StorageService
from tasks.controller import router as tasks_router
from tasks.service import TasksService
from service.models import Service, FieldDescription
from service.enums import ServiceStatus, FieldDescriptionType

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
            ]
        )

    async def process(self, data):
        # NOTE that the data is a dictionary with the keys being the field names set in the data_in_fields
        # raw = data["image"]
        # ... do something with the raw data
        raw = str(data["text"])[2:-1]
        raw = raw.replace('\\t', ',').replace('\\n', '\n').replace('\\r', '\n')
        df = pd.read_csv(io.StringIO(raw), names=["value"], dtype={"value": np.float64})
        # df.index = pd.to_datetime(df.index)
        # esd_ad = GeneralizedESDTestAD(alpha=0.3)
        # anomalies = esd_ad.fit_detect(df["value"])
        # condition = anomalies == True
        X_train = df[0:12000].to_numpy()
        X_test = df[12000:].to_numpy()
        # indexes = anomalies.index[condition]
        # result = indexes.strftime("%Y-%m-%d %H:%M:%S.%f").tolist()
        autoencoder = self.train_model(X_train)
        # Use the model to reconstruct the original time series data
        reconstructed_X = autoencoder.predict(X_test)

        # Calculate the reconstruction error for each point in the time series
        reconstruction_error = np.square(X_test - reconstructed_X).mean(axis=1)

        err = pd.DataFrame(X_test)
        fig, ax = plt.subplots(figsize=(20, 6))

        a = err.loc[reconstruction_error >= np.max(reconstruction_error)][0]  # anomaly
        # b = np.arange(35774-12000, 35874-12000)
        ax.plot(err, color='blue', label='Normal')
        # ax.scatter(b, err[35774-12000:35874-12000], color='green', label = 'Real anomaly')
        ax.scatter(a.index, a, color='red', label='Anomaly')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        # print(a)

        # task["result"] = {"image": buf.read()}

        # NOTE that the result must be a dictionary with the keys being the field names set in the data_out_fields
        return {
            "result": buf.read()
        }

    def train_model(self, X_train):
        # Preprocess the data (e.g., scale the data, create train/test splits)

        # Define the input layer
        input_layer = tf.keras.layers.Input(shape=(X_train.shape[1],))

        # Define the encoding layers
        encoded = tf.keras.layers.Dense(32, activation='relu')(input_layer)
        encoded = tf.keras.layers.Dense(16, activation='relu')(encoded)

        # Define the decoding layers
        decoded = tf.keras.layers.Dense(16, activation='relu')(encoded)
        decoded = tf.keras.layers.Dense(32, activation='relu')(decoded)

        # Define the output layer
        output_layer = tf.keras.layers.Dense(X_train.shape[1])(decoded)

        # Create the autoencoder model
        autoencoder = tf.keras.models.Model(input_layer, output_layer)

        # Compile the model
        autoencoder.compile(optimizer='adam', loss='mean_squared_error')

        # Fit the model to the time series data
        autoencoder.fit(X_train, X_train, epochs=10, batch_size=32)

        return autoencoder


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
