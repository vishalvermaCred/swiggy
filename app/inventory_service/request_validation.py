from typing import Optional
from pydantic import (
    Field,
    BaseModel,
)

from .constants import Roles, MealType


class createMenu(BaseModel):
    restaurant_id: str = Field(...)
    name: str = Field(...)
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
    name: Optional[str] = None
    description: Optional[str] = None
    price: float = Field(None)
    ordered_quantity: int = 0
    restock_quantity: int = 0
    is_available: bool = False
