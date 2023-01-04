from asyncio import Queue
from PIL import Image
from config import Settings, get_settings
from logger import Logger
from fastapi import Depends
from keras import models
from tasks.models import Task
import cv2
import numpy as np


class WorkQueue(Queue):
    async def find(self, task_id):
        for item in self._queue:
            if item['id'] == task_id:
                return item
        return None


class TasksService:
    def __init__(self, logger: Logger = Depends(), settings: Settings = Depends(get_settings)):
        self.logger = logger
        self.settings = settings
        self.logger.set_source(__name__)
        self.model = models.load_model("mnist_model.h5")
        self.tasks = WorkQueue()
        self.current_task = None
        self.current_task_data_in = None
        self.current_task_data_out = None

    async def add_task(self, task: Task):
        await self.tasks.put(task)
        self.logger.info(f"Added task {task.id} to the queue")

    async def get_task_status(self, task_id):
        if self.current_task and self.current_task['id'] == task_id:
            return self.current_task.status
        task = await self.tasks.find(task_id)
        if task is not None:
            return task.status
        else:
            return None

    async def init_task(self):
        self.current_task = self.tasks.get()
        self.current_task.status = ...
        # TODO: get the image from the storage and store in raw variable
        self.current_task_data_in = {'image': Image.open('../../tests/two.jpg')}

    async def process_task(self):
        try:
            raw = Image.open('../../tests/two.jpg')
            img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
            shape = self.model.input.shape[1]
            sz = int(np.sqrt(shape))
            resized = cv2.resize(img, (sz, sz))
            normalized = resized / 255.0
            flattened = np.reshape(normalized, [-1, shape])
            pred = self.model.predict(flattened)
            guessed = np.argmax(pred)
            self.logger.info(f"Guessed digit: {guessed}")
        except Exception as e:
            self.logger.error(f"Failed to process image: {str(e)}")

    async def end_task(self):
        self.current_task.status = ...
        # TODO: upload result to the storage and store the URL in task.data_out

    async def notify_engine(self):
        pass

    async def run(self):
        while True:
            await self.init_task()
            await self.process_task()
            await self.end_task()
            await self.notify_engine()
