import os
import asyncio
import httpx
from fastapi import FastAPI, File, UploadFile, Depends

from .worker import Worker, Callback
from . import interface
import pydantic

async def startup():
	# Announce ourself to the engine
	if engine is not None and service is not None:
		serviceDescr = {"url": service + "/compute", "api": interface.engineAPI()}
		await client.post(engine + "/services", json=serviceDescr)

	worker.chain(callback)
	callback.start()
	worker.start()

async def shutdown():
	# Remove ourself from the engine
	if engine is not None and service is not None:
		endpoint = interface.engineAPI()["route"]
		await client.delete(engine + "/services/" + endpoint)

	await worker.stop()
	await callback.stop()

engine = os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None
service = os.environ["APP_SERVICE"] if "APP_SERVICE" in os.environ else None

client = httpx.AsyncClient()
worker = Worker()
callback = Callback()
app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])

@app.post("/compute", response_model = interface.TaskId)
async def post(img: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"callback_url": callback_url, "task_id": task_id, "img": img}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)
