from enum import Enum


class MealType(Enum):
    VEG = "veg"
    NONVEG = "non-veg"


class Roles(Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    RIDER = "rider"


class Tables(Enum):
    MENU = {
        "name": "food_items",
        "columns": [
            "food_item_id",
            "restaurant_id",
            "name",
            "price",
            "stock_quantity",
            "meal_type",
            "cuisine_type",
            "description",
            "is_available",
            "rating",
        ],
    }

    RESTAURANT = {
        "name": "restaurant",
        "columns": [
            "user_id",
            "name",
            "password_hash",
            "email",
            "phone_number",
            "address",
            "pincode",
            "description",
            "pure_veg",
            "meal_type",
            "cuisine_type",
            "is_available",
            "rating",
        ],
    }
