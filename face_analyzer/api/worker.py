import asyncio
import httpx
import io
from PIL import Image
from deepface import DeepFace
import numpy as np

class Worker():
	def __init__(self, stackResult):
		self.asyncTask = None
		self.running = False
		self.queue = asyncio.Queue()
		self.next = None
		self.stackResult = stackResult

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
		print("[Worker] Processing...")
		raw = await task["img"].read()
		buff = io.BytesIO(raw)
		img_pil = Image.open(buff)
		img = np.array(img_pil)

		diagnos = DeepFace.analyze(img_path=img , actions=['age', 'gender', 'race', 'emotion'])
		res = {}
		res["age"] = diagnos["age"]
		res["region"] = diagnos["region"]
		res["race"] = diagnos["dominant_race"]
		res["emotion"] = diagnos["dominant_emotion"]
		task["result"] = { "answer": res }
		
		self.stackResult.append(task["result"])
		print("[Worker] Proscess : \n", task["result"])
		return task

class Callback(Worker):
	def __init__(self, stackResult):
		super().__init__(stackResult)
		self.client = httpx.AsyncClient()

	async def process(self, task):
		print("[Callback] Process")
		url = task["callback_url"]
		task_id = task["task_id"]
		if url is not None:
			# Needs to be modified if the result contains a blob to send back
			# something like: await self.client.post(url, params={"task_id": task_id}, files={"result": file...})
			await self.client.post(url, params={"task_id": task_id}, json=task["result"])
