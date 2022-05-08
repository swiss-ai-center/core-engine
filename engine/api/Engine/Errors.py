from fastapi import HTTPException

class ItemNotFound(HTTPException):
	def __init__(self, message):
		super().__init__(status_code=404, detail=message)

class BadStatus(HTTPException):
	def __init__(self, message):
		super().__init__(status_code=400, detail=message)

class BadID(HTTPException):
	def __init__(self, message):
		super().__init__(status_code=400, detail=message)
