from typing import Optional, List
from pydantic import (
    BaseModel,
    Field,
    validator,
    root_validator,
)

from .constants import email_regex, phone_regex, Address, Roles, MealType


class userSignUp(BaseModel):
    name: str = Field(..., min_length=1)
    role: Roles = Field(...)
    email: str = Field(..., regex=email_regex)
    phone_number: str = Field(..., regex=phone_regex)
    password_hash: str = Field(...)
    address: dict = Field(None)
    description: str = Field(None)
    pure_veg: bool = False
    meal_type: Optional[MealType] = Field(None)
    cuisine_type: List = None

    class config:
        use_enum_values = True

    @root_validator(pre=True)
    def validate_address(cls, values):
        role = values.get("role")
        address = values.get("address")
        if role != Roles.RIDER.value:
            for key in Address:
                if not address.get(key.value):
                    raise ValueError(f"{key.value} for complete address is not provided")
        return values


class CustomerSignIn(BaseModel):
    phone_number: Optional[str] = None
    role: Optional[Roles] = None

    @root_validator(pre=False)
    def validate_params(cls, values):
        phone_number = values.get("phone_number")
        role = values.get("role")
        if not (phone_number and role):
            raise ValueError("phone number and role is required")
        return values


class FetchUser(BaseModel):
    role: Optional[Roles] = None
    user_id: Optional[str] = None

    @root_validator(pre=False)
    def validate_params(cls, values):
        user_id = values.get("user_id")
        role = values.get("role")
        if not user_id:
            raise ValueError("user_id is required")
        if not role:
            raise ValueError("role is mandatory")
        return values


class AddAddresses(BaseModel):
    user_id: str = Field(..., min_length=1)
    address: dict = Field()
    role: Roles = Field(...)

    @validator("address")
    def validate_address(cls, value):
        for key in Address:
            if not value.get(key.value):
                raise ValueError(f"{key.value} for complete address is not provided")
        return value
