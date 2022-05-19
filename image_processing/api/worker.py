import asyncio
import httpx
import io
import cv2
import numpy as np
import json
import logging

from PIL import Image
from PIL.ExifTags import TAGS

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

	async def blur(self, task):
		raw = await task["image"].read()
		img = cv2.imdecode(np.frombuffer(raw, np.uint8), 1)

		raw_areas = await task["areas"].read()
		areas = json.loads(raw_areas)['areas']

		rows = img.shape[0]
		cols = img.shape[1]

		for a in areas:
			a[0] = self.clamp(int(a[0]), 0, cols)
			a[1] = self.clamp(int(a[1]), 0, rows)
			a[2] = self.clamp(int(a[2]), 0, cols)
			a[3] = self.clamp(int(a[3]), 0, rows)

		for a in areas:
			x1, x2, y1, y2 = a[0], a[2], a[1], a[3]
			# We need to compute the blur kernel size according to the area size
			areaSize = max(x2 - x1, y2 - y1)
			kernelSize = int(areaSize * 0.08)
			img[y1:y2 + 1, x1:x2 + 1] = cv2.blur(img[y1:y2 + 1, x1:x2 + 1], (kernelSize, kernelSize))

		is_success, outBuff = cv2.imencode(".jpg", img)
		task["result"] = outBuff.tobytes()
		return task

	async def analyze(self, task):
		raw = await task["image"].read()
		stream = io.BytesIO(raw)
		img = Image.open(stream)
		metadata = {}

		metadata["format"] = img.get_format_mimetype()
		metadata["width"] = img.width
		metadata["height"] = img.height

		exif = img.getexif()
		for tagId, val in exif.items():
			name = TAGS[tagId] if tagId in TAGS else "0x{tagId:x}".format(tagId=tagId)
			metadata[name] = val if type(val) in [str, int, float, bool] else str(val)

		task["result"] = metadata
		return task

	async def crop(self, task):
		raw = await task["image"].read()
		img = cv2.imdecode(np.frombuffer(raw, np.uint8), 1)
		raw_areas = await task["areas"].read()
		areas = json.loads(raw_areas)['areas']

		cropped = []

		for area in areas:
			is_success, cropped_image = cv2.imencode(".jpg", img[area[1]:area[3], area[0]:area[2]])
			cropped.append(cropped_image.tobytes())

		task["result"] = cropped if len(cropped) > 1 else cropped[0]
		return task

	async def convert(self, task):
		raw = await task["format"].read()
		spec = json.loads(raw)
		raw = await task["image"].read()
		stream = io.BytesIO(raw)
		img = Image.open(stream)

		outBuff = io.BytesIO()
		img.save(outBuff, **spec)
		outBuff.seek(0)
		task["result"] = outBuff

		return task

	async def greyscale(self, task):
		raw = await task["image"].read()
		stream = io.BytesIO(raw)
		img = Image.open(stream)

		img2 = img.convert("L")
		outBuff = io.BytesIO()
		img2.save(outBuff, format="jpeg", quality=95)
		outBuff.seek(0)
		task["result"] = outBuff

		return task

	async def resize(sefl, task):
		raw = await task["image"].read()
		img = cv2.imdecode(np.frombuffer(raw, np.uint8), 1)

		# Scaling
		raw_settings = await task["settings"].read()
		settings = json.loads(raw_settings)

		if "withRatio" in settings and settings["withRatio"] is True:
			scale_percent = settings["scale_percent"]
			width = int(img.shape[1] * scale_percent / 100)
			height = int(img.shape[0] * scale_percent / 100)
		else:
			width = settings["width"]

			if "height" in settings:
				height = settings["height"]
			else:
				ratio = width / img.shape[1]
				height = int(img.shape[0] * ratio)

		dim = (width, height)

		# resize image
		resized = cv2.resize(img, dim, interpolation=cv2.INTER_LANCZOS4)

		# Save .jpg image
		is_success, outBuff = cv2.imencode(".jpg", resized)

		task["result"] = outBuff.tobytes()

		return task

	async def process(self, task):
		try:
			if task['operation'] == 'blur':
				await self.blur(task)

			if task['operation'] == 'crop':
				await self.crop(task)

			if task['operation'] == 'convert':
				await self.convert(task)

			if task['operation'] == 'analyze':
				await self.analyze(task)

			if task['operation'] == 'greyscale':
				await self.greyscale(task)

			if task['operation'] == 'resize':
				task = await self.resize(task)

		except Exception as e:
			task["error"] = "Failed to process image: " + str(e)

		return task

# Take task et send to engine
class Callback(Worker):
	def __init__(self):
		super().__init__()
		self.client = httpx.AsyncClient()

	async def process(self, task):
		url = task["callback_url"] if "callback_url" in task else None
		task_id = task["task_id"] if "task_id" in task else None

		if url is not None:
			res = task["result"] if "result" in task else None
			if "error" in task:
				await self.client.post(url, params={"task_id": task_id}, json={"type": "error", "message": task["error"]})
			elif type(res) is dict:
				await self.client.post(url, params={"task_id": task_id}, json=res)
			elif type(res) is bytes or isinstance(res, io.IOBase):
				await self.client.post(url, params={"task_id": task_id}, files={"result": res})
			elif type(res) is list:

				files = {}
				for i in range(len(res)):
					filename = "result" + str(i)
					files[filename] = res[i]

				await self.client.post(url, params={"task_id": task_id}, files=files)
			else:
				await self.client.post(url, params={"task_id": task_id}, json={"error": "Invalid output " + str(type(res))})
		else:
			logging.getLogger("uvicorn").warning("No callback for task, skipping")
