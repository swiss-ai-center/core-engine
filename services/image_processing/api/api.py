from fastapi import FastAPI, UploadFile
import httpx
from .worker import Worker, Callback
from .cron import Timer
from . import interface
import os
import logging

async def notifyEngine():
	for operation in interface.engineAPI:
		api = interface.engineAPI[operation]
		serviceDescr = {"url": service + "/" + operation, "api": api, "type": "service"}
		try:
			res = await client.post(engine + "/services", json=serviceDescr)
			if res.status_code != 200:
				logging.getLogger("uvicorn").warning("Failed to notify the engine, request returned " + str(res.status_code))
		except Exception as e:
			logging.getLogger("uvicorn").warning("Failed to notify the engine: " + str(e))

async def startup():
	worker.chain(callback)
	callback.start()
	worker.start()

	# Announce ourself to the engine
	if engine is not None and service is not None:
		await notifyEngine()
		tick = int(os.environ["APP_NOTIFY_CRON"]) if "APP_NOTIFY_CRON" in os.environ else 30
		notifyEngineTimer = Timer(
			timeout=tick,
			callback=notifyEngine)
		notifyEngineTimer.start()
		timers.append(notifyEngineTimer)

async def shutdown():
	for timer in timers:
		timer.stop()

	await worker.stop()
	await callback.stop()

engine = os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None
service = os.environ["APP_SERVICE"] if "APP_SERVICE" in os.environ else None

client = httpx.AsyncClient()
worker = Worker()
callback = Callback()
app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])
timers = []

@app.post("/blur", response_model=interface.TaskId)
async def blur(image: UploadFile, data: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "blur", "callback_url": callback_url, "task_id": task_id, "image": image, "areas": data}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/crop", response_model=interface.TaskId)
async def crop(image: UploadFile, data: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "crop", "callback_url": callback_url, "task_id": task_id, "image": image, "areas": data}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/convert", response_model=interface.TaskId)
async def convert(image: UploadFile, data: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "convert", "callback_url": callback_url, "task_id": task_id, "image": image, "format": data}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/analyze", response_model=interface.TaskId)
async def analyze(image: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "analyze", "callback_url": callback_url, "task_id": task_id, "image": image}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/greyscale", response_model=interface.TaskId)
async def greyscale(image: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "greyscale", "callback_url": callback_url, "task_id": task_id, "image": image}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/resize", response_model=interface.TaskId)
async def resize(image: UploadFile, data: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "resize", "callback_url": callback_url, "task_id": task_id, "image": image, "settings": data}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)
