from uuid import uuid4
from http import HTTPStatus
from quart import current_app as app

from .constants import Tables

LOGGER_KEY = "app.user_service.restaurant_management"


class restaurantManager:
    def __init__(self, kwargs) -> None:
        self.user_id = kwargs.get("user_id")
        self.name = kwargs.get("name")
        self.password_hash = kwargs.get("password_hash")
        self.email = kwargs.get("email")
        self.phone_number = kwargs.get("phone_number")
        self.address = kwargs.get("address")
        self.description = kwargs.get("description")
        self.pure_veg = kwargs.get("pure_veg")
        self.rating = kwargs.get("rating")
        self.meal_type = kwargs.get("meal_type")
        self.cuisine_type = kwargs.get("cuisine_type")

    async def createRestaurant(self):
        """
        insert the new restaurant into restaurant table
        """
        app.logger.info(f"{LOGGER_KEY}.createRestaurant")
        response = {"error": None}

        if not self.user_id:
            self.user_id = uuid4()

        restaurant_columns = Tables.RESTAURANT.value["columns"]
        restaurant_columns.remove("rating")
        restaurant_columns.remove("is_available")
        restaurant_columns = ", ".join(restaurant_columns)

        self.pincode = self.address.get("pincode")
        self.address = f"{self.address.get('line')}, {self.address.get('city')}, {self.address.get('state')}"

        # preparing insert query
        insert_restaurant_query = f"INSERT INTO {Tables.RESTAURANT.value['name']} ({restaurant_columns}) VALUES ('{self.user_id}', '{self.name.lower()}', '{self.password_hash}', '{self.email}', '{self.phone_number}', '{self.address}', '{self.pincode}', "

        insert_restaurant_query += f"'{self.description}', " if self.description else f"null, "
        insert_restaurant_query += f"'{self.pure_veg}', " if self.pure_veg else f"false, "
        insert_restaurant_query += f"'{self.meal_type.value}', " if self.meal_type else f"null, "
        insert_restaurant_query += (
            f"ARRAY{self.cuisine_type}::VARCHAR[], " if self.cuisine_type else f"ARRAY[]::VARCHAR[], "
        )
        insert_restaurant_query = f"{insert_restaurant_query.strip(', ')} );"

        try:
            insert_response = await app.user_db.execute_insert_or_update_query(insert_restaurant_query)
            app.logger.info(f"{LOGGER_KEY}.createCustomer.insert_response: {insert_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.createCustomer.exception: {str(e)}")
            response["error"] = str(e)

        return response

    async def fetchRestaurant(self):
        """
        fetches restaurant data from the restaurant table
        """
        app.logger.info(f"{LOGGER_KEY}.getRestaurant")
        response = {"error": None}

        # TODO - integrate redis
        if not (self.user_id or self.phone_number):
            response["error"] = "invalid user id or mobile number"
            response["status_code"] = HTTPStatus.BAD_REQUEST.value
            return response

        restaurant_columns = ", ".join(Tables.RESTAURANT.value["columns"])
        restaurant_select_query = f"SELECT {restaurant_columns} FROM {Tables.RESTAURANT.value['name']} where "
        if self.user_id:
            restaurant_select_query += f"user_id = '{self.user_id}';"
        elif self.phone_number:
            restaurant_select_query += f"phone_number = '{self.phone_number}';"

        try:
            restaurant_data = await app.user_db.execute_raw_select_query(restaurant_select_query)
            if restaurant_data:
                restaurant_data = restaurant_data[0]
            else:
                restaurant_data = {}
            response = restaurant_data
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.fetchCustomer.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response
