from uuid import uuid4
from http import HTTPStatus
from quart import current_app as app

from .constants import Tables

LOGGER_KEY = "app.user_service.rider_management"


class riderManager:
    def __init__(self, kwargs) -> None:
        self.user_id = kwargs.get("user_id")
        self.name = kwargs.get("name")
        self.password_hash = kwargs.get("password_hash")
        self.email = kwargs.get("email")
        self.phone_number = kwargs.get("phone_number")
        self.rating = kwargs.get("rating")

    async def createRider(self):
        app.logger.info(f"{LOGGER_KEY}.createRider")
        response = {"error": None}

        if not self.user_id:
            self.user_id = uuid4().hex

        rider_columns = Tables.RIDER.value["columns"]
        rider_columns.remove("rating")
        rider_columns.remove("is_available")
        rider_columns = ", ".join(rider_columns)

        # preparing insert query
        insert_rider_query = f"INSERT INTO {Tables.RIDER.value['name']} ({rider_columns}) VALUES ('{self.user_id}', '{self.name.lower()}', '{self.password_hash}', '{self.email}', '{self.phone_number}');"

        try:
            insert_response = await app.user_db.execute_insert_or_update_query(insert_rider_query)
            app.logger.info(f"{LOGGER_KEY}.createCustomer.insert_response: {insert_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.createCustomer.exception: {str(e)}")
            response["error"] = str(e)

        return response

    async def fetchRider(self):
        app.logger.info(f"{LOGGER_KEY}.getRestaurant")
        response = {"error": None}

        # TODO - integrate redis
        if not (self.user_id or self.phone_number):
            response["error"] = "invalid user id or mobile number"
            response["status_code"] = HTTPStatus.BAD_REQUEST.value
            return response

        customer_columns = ", ".join(Tables.RIDER.value["columns"])
        customer_select_query = f"SELECT {customer_columns} FROM {Tables.RIDER.value['name']} where "
        if self.user_id:
            customer_select_query += f"user_id = '{self.user_id}';"
        elif self.phone_number:
            customer_select_query += f"phone_number = '{self.phone_number}';"

        try:
            customer_data = await app.user_db.execute_raw_select_query(customer_select_query)
            if customer_data:
                customer_data = customer_data[0]
            else:
                customer_data = {}
            response = customer_data
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.fetchCustomer.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response
