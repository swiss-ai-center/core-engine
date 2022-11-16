from fastapi import Depends
from storage import Storage
from sqlmodel import Session
from database import get_session
from logger import Logger


class PipelinesService:
    def __init__(self, logger: Logger = Depends(), storage: Storage = Depends(), session: Session = Depends(get_session)):
        self.logger = logger
        self.storage = storage
        self.session = session

    # TODO: Implement get_services method
    def get_pipelines(self):
        pipelines = None

        return pipelines

    # TODO: Implement create method
    def create(self, pipeline_name, pipeline):
        pass

    # TODO: Implement delete method
    def delete(self, pipeline_name):
        pass

    # TODO: Implement find_one method
    def find_one(self, pipeline_name):
        pipeline = None

        return pipeline
