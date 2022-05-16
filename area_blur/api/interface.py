from pydantic import BaseModel

_uid = 0

def uid():
	global _uid
	_uid += 1
	return _uid

class TaskId(BaseModel):
	task_id: str

engineAPI = {}
engineAPI["blur"] = {"route": "image-blur", "body": ["image", "areas"], "summary": "Blur one or more areas in an image"}
engineAPI["crop"] = {"route": "image-crop", "body": ["image", "areas"], "summary": "Crop one or more areas of an image"}
engineAPI["convert"] = {"route": "image-convert", "body": ["image", "format"], "summary": "Convert between image formats"}
engineAPI["resize"] = {"route": "image-resize", "body": ["image", "settings"], "summary": "Resize an image with scale percent or directly with witdh/height"}
engineAPI["analyze"] = {"route": "image-analyze", "body": ["image"], "summary": "Extract image metadata"}
engineAPI["greyscale"] = {"route": "image-greyscale", "body": ["image"], "summary": "Convert image to black and white / grey scale"}
