import asyncio
import httpx
import cv2
import numpy as np
from keras import models
from fastapi import Depends
from logger import Logger
from config import Settings, get_settings


class WorkerService:
    def __init__(self, logger: Logger = Depends(), settings: Settings = Depends(get_settings)):
        self.logger = logger
        self.settings = settings
        self.asyncTask = None
        self.running = False
        self.queue = asyncio.Queue()
        self.next = None
        self.model = models.load_model("mnist_model.h5")

    def start(self):
        self.running = True
        self.asyncTask = asyncio.create_task(self.run())

    def chain(self, worker):
        self.next = worker

    async def stop(self):
        self.running = False
        await self.queue.put(None)
        await self.asyncTask

    async def add_task(self, task):
        await self.queue.put(task)

    async def run(self):
        while self.running:
            task = await self.queue.get()
            if task is not None:
                result = await self.process(task)
                if result is not None and self.next is not None:
                    await self.next.addTask(result)

    async def process(self, task):
        try:
            raw = await task["image"].read()
            img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
            shape = self.model.input.shape[1]
            sz = int(np.sqrt(shape))
            resized = cv2.resize(img, (sz, sz))
            normalized = resized / 255.0
            flattened = np.reshape(normalized, [-1, shape])
            pred = self.model.predict(flattened)
            guessed = np.argmax(pred)
            task["result"] = {"digit": int(guessed)}
        except Exception as e:
            task["error"] = "Failed to process image: " + str(e)

        return task


class Callback(WorkerService):
    def __init__(self):
        super().__init__()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def process(self, task):
        url = task["callback_url"]
        task_id = task["task_id"]
        if url is not None:
            data = None
            if "error" in task:
                data = {"type": "error", "message": task["error"]}
            else:
                data = task["result"]
            try:
                await self.client.post(url, params={"task_id": task_id}, json=data)
            except Exception as e:
                self.logger.error(f"Failed to send response to engine: {e}")
