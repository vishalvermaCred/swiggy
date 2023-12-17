from enum import Enum


class Roles(Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    RIDER = "rider"


class OrderStatus(Enum):
    ORDER_PLACED = "order_placed"
    COOKING = "cooking"
    READY_FOR_DELIVERY = "ready_for_delivery"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Tables(Enum):
    CART = {
        "name": "cart",
        "columns": ["id", "food_item_id", "restaurant_id", "customer_id", "price", "quantity", "is_expired"],
    }

    ORDERS = {
        "name": "orders",
        "columns": [
            "order_id",
            "customer_id",
            "restaurant_id",
            "rider_id",
            "total_amount",
            "order_status",
            "delivery_time",
            "cancelled_time",
        ],
    }

    ORDER_ITEMS = {"name": "order_items", "columns": ["order_id", "food_item_id", "quantity", "price"]}
