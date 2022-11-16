from fastapi import Depends
from storage import Storage
from sqlmodel import Session
from database import get_session
from logger import Logger


class ServicesService:
    def __init__(self, logger: Logger = Depends(), storage: Storage = Depends(), session: Session = Depends(get_session)):
        self.logger = logger
        self.storage = storage
        self.session = session

    # TODO: Implement get_services method
    def get_services(self):
        services = None

        return services

    # TODO: Implement create method
    def create(self, service_name, service):
        pass

    # TODO: Implement delete method
    def delete(self, service_name):
        pass

    # TODO: Implement find_one method
    def find_one(self, service_name):
        service = None

        return service
