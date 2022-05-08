from fastapi import FastAPI, UploadFile
import httpx
from .worker import Worker, Callback
from . import interface
import os

async def startup():
	# Announce ourself to the engine
	if engine is not None and service is not None:
		serviceDescr = {"url": service + "/compute", "api": interface.engineAPI(), "type": "service"}
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

# Implement me!!! Define meaningful routes here, using input objects from "interface" or UploadFile + query params

# # This is a route for a service that only takes json input, which structure should be a interface.Job object
# @app.post("/compute", response_model = interface.TaskId)
# async def post(data: interface.Job, callback_url: str = None, task_id: str = None):
# 	if task_id is None:
# 		task_id = str(interface.uid())
# 	task = {"callback_url": callback_url, "task_id": task_id, "data": data.dict()}
# 	await worker.addTask(task)
# 	return interface.TaskId(task_id=task_id)

# This is a route for a service that takes a binary file as input, plus a custom "data1" query param
@app.post("/compute", response_model=interface.TaskId)
async def post(image: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"callback_url": callback_url, "task_id": task_id, "image": image}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)
