import asyncio
import httpx
import io
import cv2
import numpy as np
import json

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
		raw_img = await task["image"].read()
		img_strm = io.BytesIO(raw_img)
		img = cv2.imdecode(np.frombuffer(img_strm.read(), np.uint8), 1)

		raw_areas = await task["areas"].read()
		areas = json.loads(raw_areas)
		areas = areas['areas']
		task["areas"] = areas
		# [x1, y1, x2, y2]
		rows = img.shape[0]
		cols = img.shape[1]

		for a in areas:
			a[0] = self.clamp(int(a[0]), 0, cols)
			a[1] = self.clamp(int(a[1]), 0, rows)
			a[2] = self.clamp(int(a[2]), 0, cols)
			a[3] = self.clamp(int(a[3]), 0, rows)

		for a in areas:
			x1, x2, y1, y2 = a[0], a[2], a[1], a[3]
			img[y1:y2 + 1, x1:x2 + 1] = cv2.blur(img[y1:y2 + 1, x1:x2 + 1], (23, 23))
		# cv2.imwrite('res.jpg', img)
		is_success, outBuff = cv2.imencode(".jpg", img)
		task["results"] = []
		task["results"].append(outBuff.tobytes())
		# await self.client.post(url, params={"task_id": task_id}, files={"result": task["result"]})
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

	async def crop(self, task):
		raw_img = await task["image"].read()
		img_strm = io.BytesIO(raw_img)
		img = cv2.imdecode(np.frombuffer(img_strm.read(), np.uint8), 1)
		raw_areas = await task["areas"].read()
		areas = json.loads(raw_areas)
		task["areas"] = areas
		areas = areas['areas']
		task["results"] = []
		for area in areas:
			is_success, cropped_image = cv2.imencode(".jpg", img[area[0]:area[2], area[1]:area[3]])
			task["results"].append(cropped_image.tobytes())

		return task

	async def convertPNGtoJPG(sefl, task):
		raw_img = await task["image"].read()
		img_strm = io.BytesIO(raw_img)
		img = cv2.imdecode(np.frombuffer(img_strm.read(), np.uint8), 1)

		# Save .jpg image
		is_success, converted_imaged = cv2.imencode(".jpg", img)

		task["results"] = []
		task["results"].append(converted_imaged.tobytes())

		return task

	async def greyscale(self, task):
		raw = await task["image"].read()
		stream = io.BytesIO(raw)
		img = Image.open(stream)
		img2 = img.convert("L")
		outBuff = io.BytesIO()
		img2.save(outBuff, format="jpeg", quality=95)
		outBuff.seek(0)
		task["results"] = [outBuff]

	async def process(self, task):
		if task['operation'] == 'blur':
			await self.blur(task)

		if task['operation'] == 'crop':
			await self.crop(task)

		if task['operation'] == 'convertPNGtoJPG':
			await self.convertPNGtoJPG(task)

		if task['operation'] == 'analyze':
			await self.analyze(task)

		if task['operation'] == 'greyscale':
			await self.greyscale(task)

		return task

# Take task et send to engine
class Callback(Worker):
	def __init__(self):
		super().__init__()
		self.client = httpx.AsyncClient()

	async def process(self, task):
		url = task["callback_url"] if "callback_url" in task else None
		task_id = task["task_id"] if "task_id" in task else None

		jsonResult = task['operation'] == "analyze"

		if url is not None:
			if jsonResult:
				await self.client.post(url, params={"task_id": task_id}, json=task["result"])
			else:
				files = {}
				if(len(task["results"]) > 1):
					i = 1
					for result in task["results"]:
						filename = "result" + str(i)
						files[filename] = result
						i += 1
				else:
					files['result'] = task["results"][0]

				await self.client.post(url, params={"task_id": task_id}, files=files)
