from os import getenv

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
APP_NAME = "swiggy_service"
ENV = getenv("ENV", "PRODUCTION").lower()

LOG_LEVEL = getenv("LOG_LEVEL", "DEBUG")

BASE_ROUTE = getenv("BASE_ROUTE")
SERVICE_NAME = getenv("SERVICE_NAME")

HEADERS = {"Content-Type": "application/json"}
REDIS = {"HOST": getenv("REDIS_HOST"), "PORT": getenv("REDIS_PORT")}

# DB CONFIGS
USER_DB_CONFIGS = {
    "HOST": getenv("DB_HOST"),
    "PORT": getenv("DB_PORT"),
    "NAME": getenv(f"USER_DB_NAME"),
    "PASSWORD": getenv("USER_DB_PASSWORD"),
    "USER": getenv("USER_DB_USER"),
}

RESTAURANT_DB_CONFIGS = {
    "HOST": getenv("DB_HOST"),
    "PORT": getenv("DB_PORT"),
    "NAME": getenv(f"RESTAURANT_DB_NAME"),
    "PASSWORD": getenv("RESTAURANT_DB_PASSWORD"),
    "USER": getenv("RESTAURANT_DB_USER"),
}

ORDER_DB_CONFIGS = {
    "HOST": getenv("DB_HOST"),
    "PORT": getenv("DB_PORT"),
    "NAME": getenv(f"ORDER_DB_NAME"),
    "PASSWORD": getenv("ORDER_DB_PASSWORD"),
    "USER": getenv("ORDER_DB_USER"),
}

# BASE URLS
USER_SERVICE_BASE_URL = getenv("USER_SERVICE_BASE_URL")
ORDER_SERVICE_BASE_URL = getenv("ORDER_SERVICE_BASE_URL")
PAYMENT_SERVICE_BASE_URL = getenv("PAYMENT_SERVICE_BASE_URL")
DELIVERY_SERVICE_BASE_URL = getenv("DELIVERY_SERVICE_BASE_URL")
RESTAURANT_SERVICE_BASE_URL = getenv("RESTAURANT_SERVICE_BASE_URL")
