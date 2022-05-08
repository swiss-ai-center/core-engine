import asyncio
import httpx
import io
from PIL import Image
from retinaface import RetinaFace
import numpy as np

class Worker():
	def __init__(self):
		self.asyncTask = None
		self.running = False
		self.queue = asyncio.Queue()
		self.next = None

	def start(self):
		self.running = True
		self.asyncTask = asyncio.create_task(self.run())

	def chain(self, worker):
		self.next = worker

	async def stop(self):
		self.running = False
		await self.queue.put(None)
		await self.asyncTask

	async def addTask(self, task):
		await self.queue.put(task)

	async def run(self):
		while self.running:
			task = await self.queue.get()
			if task is not None:
				result = await self.process(task)
				if result is not None and self.next is not None:
					await self.next.addTask(result)

	async def process(self, task):
		# Implement me with something useful!!!
		raw = await task["image"].read()
		buff = io.BytesIO(raw)
		img_pil = Image.open(buff)
		img = np.array(img_pil)

		faces = RetinaFace.detect_faces(img)
		# cast int64 to int to fixe json error (can't convert int64)
		res = [[int(i) for i in v['facial_area']] for k, v in faces.items()]
		task["result"] = {"answer": res}
		return task

class Callback(Worker):
	def __init__(self):
		super().__init__()
		self.client = httpx.AsyncClient()

	async def process(self, task):
		url = task["callback_url"]
		task_id = task["task_id"]
		if url is not None:
			# Needs to be modified if the result contains a blob to send back
			# something like: await self.client.post(url, params={"task_id": task_id}, files={"result": file...})
			await self.client.post(url, params={"task_id": task_id}, json=task["result"])
