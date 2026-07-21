from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, field_validator
from sqlmodel import Column, Field

from common.models import CoreModel, PydanticJSON

"""
# To only give access a route to administrators :
@router.delete("/services/{id}", dependencies=[Depends(RoleChecker([Role.ADMIN]))])
# or if the route needs the user :
def create(current_user: User = Depends(RoleChecker([Role.USER, Role.ADMIN]))):
"""


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class Address(BaseModel):
    street: str
    # str, not int: house numbers like "12b" exist
    street_nbr: str
    city: str
    npa: str
    country: str


class UserBase(CoreModel):
    """
    Base class for User
    This model is used in subclasses
    """
    email: str = Field(unique=True)
    first_name: str
    last_name: str
    role: Role
    # Optional for now: only needed once we start billing users
    address: Optional[Address] = Field(sa_column=Column(PydanticJSON), default=None)


class User(UserBase, table=True):
    """
    User model
    This model is the one that is stored in the database
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # Fields required by the fastapi-users user protocol. hashed_password is
    # kept out of UserBase so it can never leak through an API response model.
    hashed_password: str
    is_active: bool = Field(default=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)


class UserRead(UserBase):
    """
    User Read model
    This model is used to return a user to the user
    """
    id: UUID


class UserNameUpdate(BaseModel):
    """Fields an authenticated user may update on their own account."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_name(cls, value):
        return value.strip() if isinstance(value, str) else value


class UserRoleUpdate(BaseModel):
    """Role change available to administrators."""

    role: Role
