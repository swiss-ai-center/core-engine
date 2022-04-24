import asyncio
import httpx
import io
import cv2
import numpy as np
from fastapi import Response
import json


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
	
	def clamp(self, val, smallest, largest):
		return max(smallest, min(val, largest))

	async def process(self, task):

		print("[Worker] Processing...")
		raw = await task["img"].read()
		img_strm = io.BytesIO(raw)
		img = cv2.imdecode(np.frombuffer(img_strm.read(), np.uint8), 1)
		
		areas = json.loads(task["areas"])
		task["areas"]=areas
		# [x1, y1, x2, y2]
		rows=img.shape[0]
		cols=img.shape[1]
		print(type(areas), areas, rows, cols)
		
		for a in areas:
			print(a)
			a[0] = self.clamp(int(a[0]), 0, cols)
			a[1] = self.clamp(int(a[1]), 0, rows)
			a[2] = self.clamp(int(a[2]), 0, cols)
			a[3] = self.clamp(int(a[3]), 0, rows)
		
		for a in areas:
			x1, x2, y1, y2 = a[0], a[2], a[1], a[3]
			img[y1:y2+1, x1:x2+1] = cv2.blur(img[y1:y2+1, x1:x2+1] ,(23,23))
		

		#cv2.imwrite('res.jpg', img)
		is_success, outBuff = cv2.imencode(".jpg", img)
		task["result"] = outBuff.tobytes()

		return task

class Callback(Worker):
	def __init__(self):
		super().__init__()
		self.client = httpx.AsyncClient()

	async def process(self, task):
		print("[Callback] Process")
		url = task["callback_url"]
		print(url)
		task_id = task["task_id"]
		if url is not None:
			# Needs to be modified if the result contains a blob to send back
			# something like: await self.client.post(url, params={"task_id": task_id}, files={"result": file...})
			await self.client.post(url, params={"task_id": task_id}, json={"areas": task["areas"]}, files={"result": task["result"]})
