import asyncio
import json
import cv2
import numpy as np
import mimetypes
from asyncio import Queue
from common.exceptions import NotFoundException
from config import Settings, get_settings
from http_client import HttpClient
from logger.logger import Logger
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from keras import models
from service.models import DigitRecognitionService

from common.exceptions import QueueFullException
from storage.service import StorageService
from tasks.enums import TaskStatus
from tasks.models import ServiceTask, TaskUpdate


def get_extension(field_description_type: str):
    """
    Get extension
    :param field_description_type: Field description type
    :return: The guessed extension
    """
    return mimetypes.guess_extension(field_description_type)


def get_mime_type(extension: str):
    """
    Get mime type
    :param extension: The extension
    :return: The mime type
    """
    return mimetypes.guess_type(extension)[0]


class WorkQueue(Queue):
    """
    A queue that add a find method to the Queue class
    """

    async def find(self, task_id):
        for item in self._queue:
            if item.task['id'] == task_id:
                return item
        return None


class TasksService:
    # TODO: Check if there is a better way than using a global variable to store the queue
    #  (and also remove the amount of tasks variable)
    tasks = WorkQueue()

    def __init__(self, logger: Logger = Depends(), settings: Settings = Depends(get_settings),
                 http_client: HttpClient = Depends(), storage: StorageService = Depends()):
        self.logger = logger
        self.logger.set_source(__name__)
        self.settings = settings
        self.http_client = http_client
        self.storage = storage
        self.service_instance = DigitRecognitionService()
        self.model = models.load_model("mnist_model.h5")
        self.running = False
        self.amount_of_tasks = 0
        # current_task is the task actually processed
        self.current_task = None
        # current_task_data_in is a dictionary containing the data downloaded from the storage used in processing
        self.current_task_data_in = dict()
        # current_task_data_out is a dictionary containing the data to be uploaded to the storage as result of the task
        self.current_task_data_out = dict()

    def is_full(self):
        """
        Check if the queue is full
        :return: True if the queue is full, False otherwise
        """
        return self.amount_of_tasks >= self.settings.max_tasks

    def start(self):
        """
        Start the service
        """
        self.running = True
        asyncio.create_task(self.run())

    async def stop(self):
        """
        Stop the service
        """
        self.running = False

    async def add_task(self, task: ServiceTask):
        """
        Add a task to the queue
        :param task: The task to add
        """
        if self.is_full():
            raise QueueFullException("Queue is full")
        await self.tasks.put(task)
        self.amount_of_tasks += 1
        self.logger.info(f"Added task {task.task.id} to the queue | Queue size: {self.tasks.qsize()}")

    async def get_task_status(self, task_id):
        """
        Get the status of a task
        :param task_id: ID of the task
        :return: The status of the task
        """
        if self.current_task and self.current_task.task['id'] == task_id:
            return self.current_task.task.status
        task = await self.tasks.find(task_id)
        if task is None:
            raise NotFoundException(f"Task {task_id} not found")
        return task.task.status

    async def init_task(self):
        """
        Get the next task from the queue
        and get the data from the storage
        """
        # Get task from the queue
        self.current_task = await self.tasks.get()
        self.logger.info(f"Got task {self.current_task} from the queue")
        self.current_task.task.status = TaskStatus.FETCHING
        data_in_desc = self.service_instance.get_data_in_fields()
        # Get the data from the storage
        for i in range(len(self.current_task.task.data_in)):
            data = await self.storage.get_file(self.current_task.task.data_in[i],
                                               self.current_task.s3_region,
                                               self.current_task.s3_secret_access_key,
                                               self.current_task.s3_access_key_id,
                                               self.current_task.s3_host,
                                               self.current_task.s3_bucket)
            print(data)
            # Creating an accepted extensions list
            accepted_extension_list = []
            for mime in data_in_desc[i]["type"]:
                accepted_extension_list.append(get_extension(mime))

            # Check if the extension is accepted
            extension = get_extension(get_mime_type(self.current_task.task.data_in[i]))
            if extension not in accepted_extension_list:
                self.logger.error(
                    f"Wrong file extension for {data_in_desc[i]['name']} ({accepted_extension_list}): got {extension}")
                self.current_task.task.status = TaskStatus.ERROR
                return

            # Each data downloaded is stored in a dictionary using api description as key, so the file list must be in
            # the same order as the api description
            self.current_task_data_in[data_in_desc[i]["name"]] = data
            self.logger.info(f"Data: {data}")
            self.logger.info(f"Got {data_in_desc[i]['name']} from the storage")

    async def process_task(self):
        """
        Processing the data
        and store the result
        """
        try:
            self.current_task.task.status = TaskStatus.PROCESSING
            self.logger.info(f"Processing task {self.current_task.task.id}")
            # Get raw image data
            raw = self.current_task_data_in["image"]
            self.logger.info(f"Got image data: {raw}")
            # Convert to image object
            image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
            # Get the shape of the model
            shape = self.model.input.shape[1]
            # Compute the size
            size = int(np.sqrt(shape))
            # Resize the image to the size of the model
            resized = cv2.resize(image, (size, size))
            # Normalize the image
            normalized = resized / 255.0
            # Reshape the image
            flattened = np.reshape(normalized, [-1, shape])
            # Predict the image
            prediction = self.model.predict(flattened)
            # Get the index of the highest probability
            guessed = np.argmax(prediction)
            # Save the result in a type that can be encoded later (str, json, ...)
            self.current_task_data_out["digit"] = str(guessed)
        except Exception as e:
            self.logger.error(f"Failed to process image: {str(e)}")
            self.current_task.task.status = TaskStatus.ERROR

    async def end_task(self):
        """
        Update the task status
        and store the result on S3
        """
        self.current_task.task.status = TaskStatus.SAVING
        try:
            for ext in self.service_instance.get_data_out_fields():
                data_bytes = self.current_task_data_out[ext["name"]].encode()
                key = await self.storage.upload(data_bytes,
                                                get_extension(ext["type"][0]),
                                                self.current_task.s3_region,
                                                self.current_task.s3_secret_access_key,
                                                self.current_task.s3_access_key_id,
                                                self.current_task.s3_host,
                                                self.current_task.s3_bucket)
                if self.current_task.task.data_out is None:
                    self.current_task.task.data_out = []
                self.current_task.task.data_out.append(key)
            self.current_task.task.status = TaskStatus.FINISHED
        except Exception as e:
            self.logger.error(f"Failed to save result: {str(e)}")
            self.current_task.task.status = TaskStatus.ERROR
        finally:
            self.amount_of_tasks -= 1

    async def notify_engine(self):
        """
        Notify the engine that the task is finished
        """
        url = f"{self.settings.engine}/tasks/{self.current_task.task.id}"
        try:
            # Encode the task to json
            data = jsonable_encoder(
                TaskUpdate(status=self.current_task.task.status, data_out=self.current_task.task.data_out))
            self.logger.info(f"Updating task {self.current_task.task.id} on engine {url}: {data}")
            # Send the update to the engine
            await self.http_client.patch(url, json=data)
            self.logger.info(f"Task {self.current_task.task.id} updated on engine")
        except Exception as e:
            self.logger.warning("Failed to send back result (" + url + "): " + str(e))

    async def run(self):
        """
        Main loop of the service
        """
        self.logger.info("Started tasks service")
        while self.running:
            await self.init_task()
            if self.current_task is None:
                await asyncio.sleep(1)
                continue
            await self.process_task()
            await self.end_task()
            await self.notify_engine()
