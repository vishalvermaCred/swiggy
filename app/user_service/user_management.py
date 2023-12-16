from http import HTTPStatus
from quart import current_app as app

LOGGER_KEY = "app.user_service"

from .constants import Roles
from app.user_service.customer_management import customerManager
from app.user_service.restaurant_management import restaurantManager
from app.user_service.rider_management import riderManager


class userManager:
    def __init__(self, kwargs) -> None:
        self.payload = kwargs
        self.role = kwargs.get("role")

    async def getUser(self, fetch_user_with_address=False):
        app.logger.info(f"{LOGGER_KEY}.getUser")

        if self.role.value == Roles.CUSTOMER.value:
            customer_manager = customerManager(self.payload)
            return await customer_manager.fetchCustomer(fetch_user_with_address)
        elif self.role.value == Roles.RESTAURANT.value:
            restaurant_manager = restaurantManager(self.payload)
            return await restaurant_manager.fetchRestaurant()
        elif self.role.value == Roles.RIDER.value:
            rider_manager = riderManager(self.payload)
            return await rider_manager.fetchRider()
        else:
            return {"error": "invalid role type provided", "status_code": HTTPStatus.BAD_REQUEST.value}

    async def createUser(self):
        app.logger.info(f"{LOGGER_KEY}.createUser")

        app.logger.info(f"{LOGGER_KEY}.getUser")

        if self.role.value == Roles.CUSTOMER.value:
            customer_manager = customerManager(self.payload)
            return await customer_manager.createCustomer()
        elif self.role.value == Roles.RESTAURANT.value:
            restaurant_manager = restaurantManager(self.payload)
            return await restaurant_manager.createRestaurant()
        elif self.role.value == Roles.RIDER.value:
            rider_manager = riderManager(self.payload)
            return await rider_manager.createRider()
        else:
            return {"error": "invalid role type provided", "status_code": HTTPStatus.BAD_REQUEST.value}
