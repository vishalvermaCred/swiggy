from uuid import uuid4
from http import HTTPStatus
from quart import current_app as app

from .constants import Tables
from app.user_service.address_mangement import Address

LOGGER_KEY = "app.user_service.customer_management"


class customerMangaer:
    def __init__(self, kwargs) -> None:
        self.user_id = kwargs.get("user_id")
        self.name = kwargs.get("name")
        self.phone_number = kwargs.get("phone_number")
        self.email = kwargs.get("email")
        self.address = kwargs.get("address", {})
        self.password_hash = kwargs.get("password_hash")

    async def createCustomer(self):
        app.logger.info(f"{LOGGER_KEY}.createCustomer")
        response = {"error": None}

        if not self.user_id:
            self.user_id = uuid4().hex

        self.address["user_id"] = self.user_id
        address = Address(self.address)

        user_columns = ", ".join(Tables.CUSTOMER.value["columns"])

        # preparing insert query
        insert_user_query = f"INSERT INTO {Tables.CUSTOMER.value['name']} ({user_columns}) VALUES ('{self.user_id}', '{self.name}', '{self.password_hash}', '{self.email}', '{self.phone_number}');"

        address_insert_query = address.form_address_insert_query()

        transaction_query = f"BEGIN; {insert_user_query} {address_insert_query} COMMIT;"

        try:
            insert_response = await app.user_db.execute_raw_transaction_query(transaction_query)
            app.logger.info(f"{LOGGER_KEY}.createCustomer.insert_response: {insert_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.createCustomer.exception: {str(e)}")
            response["error"] = str(e)

        return response

    async def fetchCustomer(self, fetch_user_with_address=False):
        app.logger.info(f"{LOGGER_KEY}.fetchCustomer")
        response = {"error": None}

        # TODO - integrate redis
        if not (self.user_id or self.phone_number):
            response["error"] = "invalid user id or mobile number"
            response["status_code"] = HTTPStatus.BAD_REQUEST.value
            return response

        customer_columns = ", ".join(Tables.CUSTOMER.value["columns"])
        customer_select_query = f"SELECT {customer_columns} FROM {Tables.CUSTOMER.value['name']} where "
        if self.user_id:
            customer_select_query += f"user_id = '{self.user_id}';"
        elif self.phone_number:
            customer_select_query += f"phone_number = '{self.phone_number}';"

        try:
            customer_data = await app.user_db.execute_raw_select_query(customer_select_query)
            response = customer_data[0]

            if fetch_user_with_address:
                self.address["user_id"] = response.get("user_id")
                address = Address(self.address)
                customer_address = await address.fetch_address()
                response["address"] = customer_address
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.fetchCustomer.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def insert_address(self):
        app.logger.info(f"{LOGGER_KEY}.insert_address")
        response = {"error": None}

        self.address["user_id"] = self.user_id
        address_manager = Address(self.address)
        insert_query = address_manager.form_address_insert_query()
        try:
            insert_response = await app.user_db.execute_insert_or_update_query(insert_query)
            app.logger.info(f"{LOGGER_KEY}.insert_address.response: {insert_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.insert_address.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value

        return response
