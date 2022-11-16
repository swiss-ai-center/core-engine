from pydantic import BaseModel

from common.models.api_description import APIDescription
from ..models.pipeline import PipelineModel


class PipelineSchema(BaseModel):
    pipeline_id: int
    url: str
    api: APIDescription

    @staticmethod
    def toPipelineSchema(pipeline_model: PipelineModel):
        return PipelineSchema(pipeline_id=pipeline_model.id)
