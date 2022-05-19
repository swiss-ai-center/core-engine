import os
import httpx
import logging
from fastapi import FastAPI, UploadFile

from .worker import Worker, Callback
from . import interface

async def startup():
	# Announce ourself to the engine
	if engine is not None and service is not None:
		serviceDescr = {"url": service + "/compute", "api": interface.engineAPI(), "type": "service"}
		try:
			res = await client.post(engine + "/services", json=serviceDescr)
			if res.status_code != 200:
				logging.getLogger("uvicorn").warning("Failed to notify the engine, request returned " + str(res.status_code))
		except Exception as e:
			logging.getLogger("uvicorn").warning("Failed to notify the engine: " + str(e))

	worker.chain(callback)
	callback.start()
	worker.start()

async def shutdown():
	# Remove ourself from the engine
	if engine is not None and service is not None:
		endpoint = interface.engineAPI()["route"]
		try:
			res = await client.delete(engine + "/services/" + endpoint)
			if res.status_code != 200:
				logging.getLogger("uvicorn").warning("Failed to notify the engine, request returned " + str(res.status_code))
		except Exception as e:
			logging.getLogger("uvicorn").warning("Failed to notify the engine: " + str(e))

	await worker.stop()
	await callback.stop()

engine = os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None
service = os.environ["APP_SERVICE"] if "APP_SERVICE" in os.environ else None

client = httpx.AsyncClient()
worker = Worker()
callback = Callback()
app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])

@app.post("/compute", response_model=interface.TaskId)
async def post(image: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"callback_url": callback_url, "task_id": task_id, "image": image}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)
