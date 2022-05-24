import os
import json
import pytest
import asyncio
import hashlib

from fastapi.testclient import TestClient
from api.api import app, startup

client = TestClient(app)
jobId = None

def path(name):
	return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

def load(name):
	f = open(path(name), "rt")
	data = json.load(f)
	f.close()
	return data

def checksum(data):
	res = hashlib.sha512(data)
	return res.hexdigest()

@pytest.fixture(scope="session")
def event_loop():
	loop = asyncio.get_event_loop()
	yield loop
	loop.close()

@pytest.fixture(scope="session", autouse=True)
@pytest.mark.asyncio
async def test_setup():
	await startup()

def test_root_notfound():
	response = client.get("/")
	assert response.status_code == 404

def test_docs():
	response = client.get("/docs")
	assert response.status_code == 200

def test_bad_pipeline():
	response = client.post("/services", json={"bad": "field"})
	assert response.status_code == 422

def test_job_without_pipeline():
	response = client.post("/services/dummy", json={"param": 432})
	assert response.status_code == 405

def test_create_pipeline():
	response = client.post("/services", json=load("dummypipeline1.json"))
	assert response.status_code == 200

def test_services():
	response = client.get("/services")
	assert response.status_code == 200
	data = response.json()
	assert len(data) == 1

@pytest.mark.asyncio
async def test_job_with_pipeline():
	global jobId
	response = client.post("/services/dummy", json={"param": 432})
	assert response.status_code == 200
	data = response.json()
	assert "jobId" in data
	jobId = data["jobId"]
	await asyncio.sleep(2)

def test_job_status():
	response = client.get("/tasks/" + jobId + "/status")
	assert response.status_code == 200
	data = response.json()
	assert "status" in data
	assert data["status"] == "finished"

def test_job_result():
	response = client.get("/tasks/" + jobId)
	assert response.status_code == 200
	data = response.json()
	assert data["param"] == 432

def test_create_pipeline_bin():
	response = client.post("/services", json=load("dummypipeline2.json"))
	assert response.status_code == 200

@pytest.mark.asyncio
async def test_job_with_pipeline_bin():
	global jobId
	f = open(path("test.jpg"), "rb")
	response = client.post("/services/dummy2", files={"img": f})
	assert response.status_code == 200
	data = response.json()
	assert "jobId" in data
	jobId = data["jobId"]
	await asyncio.sleep(2)

def test_job_status_bin():
	response = client.get("/tasks/" + jobId + "/status")
	assert response.status_code == 200
	data = response.json()
	assert "status" in data
	assert data["status"] == "finished"

def test_job_result_bin():
	response = client.get("/tasks/" + jobId)
	assert response.status_code == 200
	data = response.json()
	assert "img" in data

def test_job_result_file():
	response = client.get("/tasks/" + jobId + "/files/img")
	assert response.status_code == 200
	assert type(response.content) is bytes
	f = open(path("test.jpg"), "rb")
	origChecksum = checksum(f.read())
	f.close()
	finalChecksum = checksum(response.content)
	assert origChecksum == finalChecksum

def test_stats():
	response = client.get("/stats")
	assert response.status_code == 200
	data = response.json()
	assert "services" in data
	assert "dummy" in data["services"]
	assert data["services"]["dummy"] == 1
	assert "dummy2" in data["services"]
	assert data["services"]["dummy2"] == 1
	assert "jobs" in data
	assert data["jobs"]["total"] == 2
	assert data["jobs"]["finished"] == 2

def test_create_service():
	response = client.post("/services", json=load("dummyservice1.json"))
	assert response.status_code == 200

def test_delete_service():
	response = client.delete("/services/dummyService")
	assert response.status_code == 200
