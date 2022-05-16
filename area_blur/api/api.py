from fastapi import FastAPI, UploadFile
import httpx
from .worker import Worker, Callback
from . import interface
import os

async def startup():
	# Announce ourself to the engine
	if engine is not None and service is not None:
		for operation in interface.engineAPI:
			api = interface.engineAPI[operation]
			serviceDescr = {"url": service + "/" + operation, "api": api, "type": "service"}
			await client.post(engine + "/services", json=serviceDescr)

	worker.chain(callback)
	callback.start()
	worker.start()

async def shutdown():
	# Remove ourself from the engine
	if engine is not None and service is not None:
		for operation in interface.engineAPI:
			await client.delete(engine + "/services/" + operation)

	await worker.stop()
	await callback.stop()

engine = os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None
service = os.environ["APP_SERVICE"] if "APP_SERVICE" in os.environ else None

client = httpx.AsyncClient()
worker = Worker()
callback = Callback()
app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])

res = []

@app.post("/blur", response_model=interface.TaskId)
async def blur(image: UploadFile, areas: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "blur", "callback_url": callback_url, "task_id": task_id, "image": image, "areas": areas}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/crop", response_model=interface.TaskId)
async def crop(image: UploadFile, areas: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "crop", "callback_url": callback_url, "task_id": task_id, "image": image, "areas": areas}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/convert", response_model=interface.TaskId)
async def convert(image: UploadFile, format: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"operation": "convert", "callback_url": callback_url, "task_id": task_id, "image": image, "format": format}
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
