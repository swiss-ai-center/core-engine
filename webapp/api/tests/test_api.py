import sys, os

from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_read_main():
	response = client.get("/")
	assert response.status_code == 200
