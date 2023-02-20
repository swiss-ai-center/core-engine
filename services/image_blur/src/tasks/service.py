import asyncio
import mimetypes
from asyncio import Queue
from common.exceptions import NotFoundException
from config import Settings, get_settings
from http_client import HttpClient
from logger.logger import Logger
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from service.models import Service
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
            if item.task.id == task_id:
                return item
        return None


class TasksService:
    # TODO: Check if there is a better way than using a global variable to store the queue
    # (and also remove the amount of tasks variable)
    tasks = WorkQueue()

    running = False

    amount_of_tasks = 0

    # The task actually processed
    current_task = None

    # A dictionary containing the data downloaded from the storage used in processing
    current_task_data_in = dict()

    # A dictionary containing the data to be uploaded to the storage as result of the task
    current_task_data_out = dict()

    def __init__(
            self,
            logger: Logger = Depends(),
            settings: Settings = Depends(get_settings),
            http_client: HttpClient = Depends(),
            storage: StorageService = Depends(),
    ):
        self.logger = logger
        self.settings = settings
        self.http_client = http_client
        self.storage = storage
        self.logger.set_source(__name__)

    def set_service(self, my_service: Service):
        self.my_service = my_service

    def is_full(self):
        """
        Check if the queue is full
        :return: True if the queue is full, False otherwise
        """
        return TasksService.amount_of_tasks >= self.settings.max_tasks

    def start(self):
        """
        Start the service
        """
        TasksService.running = True
        asyncio.create_task(self.run())

    async def stop(self):
        """
        Stop the service
        """
        TasksService.running = False

    async def add_task(self, task: ServiceTask):
        """
        Add a task to the queue
        :param task: The task to add
        """
        if self.is_full():
            raise QueueFullException("Queue is full")

        await TasksService.tasks.put(task)
        TasksService.amount_of_tasks += 1
        self.logger.info(f"Added task {task.task.id} to the queue | Queue size: {TasksService.tasks.qsize()}")

    async def get_task_status(self, task_id):
        """
        Get the status of a task
        :param task_id: ID of the task
        :return: The status of the task
        """
        if TasksService.current_task and TasksService.current_task.task.id == task_id:
            return TasksService.current_task.task.status

        task = await TasksService.tasks.find(task_id)

        if task is None:
            raise NotFoundException(f"Task {task_id} not found")

        return task.task.status

    async def init_task(self):
        """
        Get the next task from the queue
        and get the data from the storage
        """
        # Get task from the queue
        TasksService.current_task = await TasksService.tasks.get()
        self.logger.info(f"Got task {TasksService.current_task} from the queue")
        TasksService.current_task.task.status = TaskStatus.FETCHING

        data_in_fields = self.my_service.get_data_in_fields()
        data_in_urls = TasksService.current_task.task.data_in

        # Iterate over the two lists at the same time
        for data_in_field, data_in_url in zip(data_in_fields, data_in_urls):
            allowed_file_types_enum = data_in_field["type"]
            allowed_file_types_list = [allowed_file_type.value for allowed_file_type in allowed_file_types_enum]

            file_type = get_mime_type(data_in_url)

            if file_type not in allowed_file_types_list:
                self.logger.error(
                    f"Wrong file extension for {data_in_field['name']} ({allowed_file_types_list}): got {file_type}"
                )
                TasksService.current_task.task.status = TaskStatus.ERROR
                return

            file = await self.storage.get_file(
                data_in_url,
                TasksService.current_task.s3_region,
                TasksService.current_task.s3_secret_access_key,
                TasksService.current_task.s3_access_key_id,
                TasksService.current_task.s3_host,
                TasksService.current_task.s3_bucket,
            )

            # Each data downloaded is stored in a dictionary using api description as key, so the file list must be in
            # the same order as the api description
            self.current_task_data_in[data_in_field["name"]] = file
            self.logger.info(f"Got {data_in_field['name']} from the storage")

    async def process_task(self):
        """
        Processing the data
        and store the result
        """
        TasksService.current_task.task.status = TaskStatus.PROCESSING
        self.logger.info(f"Processing task {TasksService.current_task.task.id}")
        try:
            TasksService.current_task_data_out = await self.my_service.process(TasksService.current_task_data_in)
        except Exception as e:
            self.logger.error(f"Failed to process image: {str(e)}")
            TasksService.current_task.task.status = TaskStatus.ERROR

    async def end_task(self):
        """
        Update the task status
        and store the result on S3
        """
        TasksService.current_task.task.status = TaskStatus.SAVING

        data_out_fields = self.my_service.get_data_out_fields()

        try:
            for data_out_field in data_out_fields:
                field_name = data_out_field["name"]
                field_type = data_out_field["type"][0]

                data = TasksService.current_task_data_out[field_name]
                file_extension = get_extension(field_type)

                key = await self.storage.upload(
                    data,
                    file_extension,
                    TasksService.current_task.s3_region,
                    TasksService.current_task.s3_secret_access_key,
                    TasksService.current_task.s3_access_key_id,
                    TasksService.current_task.s3_host,
                    TasksService.current_task.s3_bucket,
                )

                if TasksService.current_task.task.data_out is None:
                    TasksService.current_task.task.data_out = []

                TasksService.current_task.task.data_out.append(key)
                TasksService.current_task.task.status = TaskStatus.FINISHED
        except Exception as e:
            self.logger.error(f"Failed to save result: {str(e)}")
            TasksService.current_task.task.status = TaskStatus.ERROR
        finally:
            TasksService.amount_of_tasks -= 1

    async def notify_engine(self):
        """
        Notify the engine that the task is finished
        """
        url = f"{self.settings.engine_url}/tasks/{TasksService.current_task.task.id}"

        try:
            # Encode the task to json
            data = jsonable_encoder(
                TaskUpdate(
                    status=TasksService.current_task.task.status,
                    data_out=TasksService.current_task.task.data_out,
                ),
            )

            self.logger.info(f"Updating task {TasksService.current_task.task.id} on engine {url}: {data}")

            # Send the update to the engine
            await self.http_client.patch(url, json=data)
            self.logger.info(f"Task {TasksService.current_task.task.id} updated on engine")
        except Exception as e:
            self.logger.warning(f"Failed to send back result ({url}): {str(e)}")
        finally:
            TasksService.current_task = None
            TasksService.current_task_data_in = dict()
            TasksService.current_task_data_out = dict()

    async def run(self):
        """
        Main loop of the service
        """
        self.logger.info("Started tasks service")

        while TasksService.running:
            await self.init_task()

            if TasksService.current_task is None:
                # TODO: There should better ways to handle this.
                # This is a performance issue.
                await asyncio.sleep(1)
                continue

            await self.process_task()
            await self.end_task()
            await self.notify_engine()
