import os
import uvicorn
import requests

from api import interface

def main():
	host = os.environ["APP_HOST"] if "APP_HOST" in os.environ else "0.0.0.0"
	port = int(os.environ["APP_PORT"]) if "APP_PORT" in os.environ else 8080
	engine = os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None
	log = os.environ["APP_LOG"] if "APP_LOG" in os.environ else "info"

	if engine is not None:
		try:
			requests.post(engine, json=interface.engineAPI())
		except:
			print("Failed to notify engine")
	uvicorn.run("api.api:app", host=host, port=port, log_level=log)

if __name__ == "__main__":
	main()
