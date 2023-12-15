from enum import Enum

# regex of phone and email to validate the received phone number and email
phone_regex = r"^(0\d{10}|[1-9]\d{9,11})$"
email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class Roles(Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    RIDER = "rider"


class Address(Enum):
    LINE = "line"
    CITY = "city"
    STATE = "state"
    PINCODE = "pincode"


class MealType(Enum):
    VEG = "veg"
    NONVEG = "non-veg"


class Tables(Enum):
    CUSTOMER = {"name": "customer", "columns": ["user_id", "name", "password_hash", "email", "phone_number", "rating"]}

    ADDRESSES = {
        "name": "addresses",
        "columns": ["address_id", "user_id", "line", "city", "state", "pincode", "latitude", "longitude"],
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

    RIDER = {
        "name": "rider",
        "columns": ["user_id", "name", "password_hash", "email", "phone_number", "is_available", "rating"],
    }
