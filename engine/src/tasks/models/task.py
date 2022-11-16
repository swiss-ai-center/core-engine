from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from database import Base

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
