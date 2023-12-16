from typing import Optional
from pydantic import Field, BaseModel, root_validator

from .constants import Roles, MealType


class createMenu(BaseModel):
    restaurant_id: str = Field(...)
    food_item_name: str = Field(...)
    description: Optional[str] = None
    price: float = Field(None)
    stock_quantity: int = 0
    is_available: bool = False
    role: Roles = Field(...)
    meal_type: MealType = Field(...)
    cuisine_type: str = Field(...)


class fetchMenu(BaseModel):
    restaurant_id: str = None
    role: Optional[Roles] = None


class UpdateMenu(BaseModel):
    role: Roles = Field(...)
    food_item_id: str = Field(...)
    user_id: Optional[str] = None
    food_item_name: Optional[str] = None
    description: Optional[str] = None
    price: float = Field(None)
    ordered_quantity: int = 0
    restock_quantity: int = 0
    is_available: bool = False


class Search(BaseModel):
    role: Optional[Roles] = None
    food_item_name: Optional[str] = None
    price_range: Optional[str] = None
    cuisine_type: Optional[str] = None
    meal_type: Optional[MealType] = None
    rating: Optional[str] = None
    restaurant_id: Optional[str] = None
    restaurant_name: Optional[str] = None

    @root_validator(pre=False)
    def validate_params(cls, values):
        role = values.get("role")
        food_item_name = values.get("food_item_name")
        restaurant_name = values.get("restaurant_name")
        cuisine_type = values.get("cuisine_type")
        if not role:
            raise ValueError(f"role is mandatory")
        if not (food_item_name or restaurant_name):
            raise ValueError(f"please provide food item name or restaurant name")
        if cuisine_type:
            values["cuisine_type"] = cuisine_type.split(",")
        return values


class UpdateAvailabilty(BaseModel):
    role: Roles = Field(...)
    restaurant_id: str = Field(...)
    is_available: bool = Field(...)
