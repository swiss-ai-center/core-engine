from typing import List
from pydantic.main import BaseModel


class APIDescription(BaseModel):
    route: str
    summary: str | None
    description: str | None
    body: str | dict | List[str]
    bodyType: str | List[str] | None
    resultType: str | None
