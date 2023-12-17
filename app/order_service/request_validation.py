from typing import Optional
from pydantic import (
    Field,
    BaseModel,
    root_validator,
)

from .constants import Roles, OrderStatus


class AddItemToCart(BaseModel):
    food_item_id: str = Field(...)
    restaurant_id: str = Field(...)
    customer_id: str = Field(...)
    price: float = Field(...)
    role: Roles = Field(...)


class DeleteItemFromCart(BaseModel):
    food_item_id: str = Field(...)
    restaurant_id: str = Field(...)
    customer_id: str = Field(...)
    role: Roles = Field(...)


class GetCartTotal(BaseModel):
    role: Optional[Roles] = None
    customer_id: Optional[str] = None

    @root_validator(pre=False)
    def validate_params(cls, values):
        role = values.get("role")
        customer_id = values.get("customer_id")

        if not role:
            raise ValueError("role is required")
        if not customer_id:
            raise ValueError("customer_id is required")
        return values


class PlaceOrder(BaseModel):
    role: Roles = Field(...)
    customer_id: str = Field(...)
    restaurant_id: str = Field(...)
    payment_info: dict = Field(None)


class UpdateOrder(BaseModel):
    role: Roles = Field(...)
    order_status: OrderStatus = Field(...)
    restaurant_id: str = Field(None)
    rider_id: str = Field(None)
    order_id: str = Field(...)

    @root_validator(pre=True)
    def validate_payload(cls, values):
        role = values.get("role")
        order_status = values.get("order_status")
        restaurant_id = values.get("restaurant_id")
        rider_id = values.get("rider_id")

        if role == Roles.RESTAURANT.value:
            if order_status not in [
                OrderStatus.COOKING.value,
                OrderStatus.READY_FOR_DELIVERY.value,
                OrderStatus.CANCELLED.value,
            ]:
                raise ValueError(f"restaurant can only set order status to cooking and ready to deliver")
            if not restaurant_id:
                raise ValueError("restaurant id required")

        if role == Roles.RIDER.value:
            if order_status not in [
                OrderStatus.OUT_FOR_DELIVERY.value,
                OrderStatus.DELIVERED.value,
                OrderStatus.CANCELLED.value,
            ]:
                raise ValueError("rider can only set order status to out for delivery, delivered and cancelled")
            if not rider_id:
                raise ValueError("rider id required")

        if role == Roles.CUSTOMER.value:
            raise ValueError("invalid role")

        return values


class OrderHistory(BaseModel):
    role: Optional[Roles] = None
    customer_id: Optional[str] = None
    restaurant_id: Optional[str] = None
    rider_id: Optional[str] = None

    @root_validator(pre=True)
    def validate_params(cls, values):
        role = values.get("role")
        customer_id = values.get("customer_id")
        restaurant_id = values.get("restaurant_id")
        rider_id = values.get("rider_id")

        if role == Roles.RESTAURANT.value and not restaurant_id:
            raise ValueError("restaurant id required")
        if role == Roles.CUSTOMER.value and not customer_id:
            raise ValueError("customer id required")
        if role == Roles.RIDER.value and not rider_id:
            raise ValueError("rider id required")

        return values


class UpdateRider(BaseModel):
    rider_id: str = Field(...)
    order_id: str = Field(...)
