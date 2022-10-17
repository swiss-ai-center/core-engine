from pydantic import BaseModel

_uid = 0


def uid():
    global _uid
    _uid += 1
    return _uid


class TaskId(BaseModel):
    task_id: str


engineAPI = {
    "blur": {
        "route": "image-blur", "body": ["image", "areas"],
        "bodyType": ["[image/png, image/jpeg, image/jpg]", "[application/json]"],
        "resultType": ["[image/png, image/jpeg, image/jpg]"],
        "summary": "Blur one or more areas in an image"
    },
    "crop": {
        "route": "image-crop", "body": ["image", "areas"],
        "bodyType": ["[image/jpeg, image/jpg]", "[application/json]"],
        "resultType": ["[image/jpeg, image/jpg]"],
        "summary": "Crop one or more areas of an image"
    },
    "convert": {
        "route": "image-convert", "body": ["image", "format"],
        "bodyType": ["[image/png, image/jpeg, image/jpg]", "[application/json]"],
        "resultType": ["[image/png, image/jpeg, image/jpg]"],
        "summary": "Convert between image formats"},
    "resize": {
        "route": "image-resize", "body": ["image", "settings"],
        "bodyType": ["[image/png, image/jpeg, image/jpg]", "[application/json]"],
        "resultType": ["[image/png, image/jpeg, image/jpg]"],
        "summary": "Resize an image with scale percent or directly with witdh/height"
    },
    "analyze": {
        "route": "image-analyze", "body": ["image"],
        "bodyType": ["[image/png, image/jpeg, image/jpg]"],
        "resultType": ["[application/json]"],
        "summary": "Extract image metadata"
    },
    "greyscale": {
        "route": "image-greyscale", "body": ["image"],
        "bodyType": ["[image/png, image/jpeg, image/jpg]"],
        "resultType": ["[image/png, image/jpeg, image/jpg]"],
        "summary": "Convert image to black and white / grey scale"
    }
}
