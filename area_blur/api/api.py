from fastapi import FastAPI, UploadFile
import httpx
from .worker import Worker, Callback
from . import interface
import os
import io
import base64


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

res = []


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
async def post(data: UploadFile, image: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"callback_url": callback_url, "task_id": task_id, "image": image, "areas": data}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/result", response_model=interface.TaskId)
async def result_post(image: UploadFile, task_id: str = None):
	raw_img = await image.read()
	img_strm = io.BytesIO(raw_img)
	buff = img_strm
	img_str = base64.b64encode(buff.getvalue())
	res.append(img_str)
	return interface.TaskId(task_id="-1")

@app.get("/result", response_model=interface.TaskId)
async def result_get():
	img_str = res.pop()
	return interface.TaskId(task_id=f'<img src="data:image/jpg;base64, {img_str}/>')
