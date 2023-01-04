from pydantic import BaseModel


class FileBase(BaseModel):
    """
    Base class for File
    This model is used in subclasses
    """
    key: str


class File(FileBase):
    """
    File model
    """
    pass


class FileRead(FileBase):
    """
    File read model
    This model is used to return a file to the user
    """
    pass
