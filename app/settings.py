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

USER_DB_CONFIGS = {
    "HOST": getenv("DB_HOST"),
    "PORT": getenv("DB_PORT"),
    "NAME": getenv(f"USER_DB_NAME"),
    "PASSWORD": getenv("USER_DB_PASSWORD"),
    "USER": getenv("USER_DB_USER"),
}
