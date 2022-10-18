from pydantic import BaseModel

_uid = 0


def uid():
    global _uid
    _uid += 1
    return _uid


class TaskId(BaseModel):
    task_id: str


# if the service has only one route
def engineAPI():
    return {
        "route": "SAMPLE-SERVICE", "body": ["param1", "param2", "..."],
        "bodyType": ["[image/png, image/jpeg, image/jpg]", "type2", "..."],
        "resultType": ["[image/png, image/jpeg, image/jpg]", "type2", "..."],
        "summary": "Describe the service here..."
    }

# else if the service has multiple routes
# engineAPI = {
#   "route1": {
#       "route": "SAMPLE-SERVICE", "body": ["param1", "param2", "..."],
#       "bodyType": ["[image/png, image/jpg]", "type2", "..."],
#       "resultType": ["[image/png, image/jpg]", "type2", "..."],
#       "summary": "Describe the service here..."
#   },
#   "route2": {
#       "route": "SAMPLE-SERVICE-2", "body": ["param1", "param2", "..."],
#       "bodyType": ["[image/png, image/jpg]", "type2", "..."],
#       "resultType": ["[image/png, image/jpg]", "type2", "..."],
#       "summary": "Describe the service here..."
#   },
