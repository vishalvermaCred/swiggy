from uuid import uuid4
from quart import current_app as app

from .constants import Tables

LOGGER_KEY = "app.user_service.address_management"


class Address:
    def __init__(self, kwargs) -> None:
        self.address_id = kwargs.get("address_id")
        self.user_id = kwargs.get("user_id")
        self.line = kwargs.get("line")
        self.city = kwargs.get("city")
        self.state = kwargs.get("state")
        self.pincode = kwargs.get("pincode")
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")

    def formAddressInsertQuery(self):
        """
        returns the insert query for address_table
        """
        app.logger.info(f"{LOGGER_KEY}.formAddressInsertQuery")
        if not self.address_id:
            self.address_id = uuid4().hex

        table_name = Tables.ADDRESSES.value["name"]
        columns = ", ".join(Tables.ADDRESSES.value["columns"])
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ('{self.address_id}', '{self.user_id}', '{self.line}', '{self.city}', '{self.state}', '{self.pincode}', "

        insert_query += f"'{self.latitude}', " if self.latitude else f"null, "
        insert_query += f"'{self.longitude}', " if self.longitude else f"null, "
        insert_query = f"{insert_query.strip(', ')} );"
        return insert_query

    async def fetchAddress(self):
        """
        fetches the customer address
        """
        app.logger.info(f"{LOGGER_KEY}.fetchAddress")

        address_columns = ", ".join(Tables.ADDRESSES.value["columns"])
        address_select_query = (
            f"SELECT {address_columns} FROM {Tables.ADDRESSES.value['name']} WHERE user_id = '{self.user_id}';"
        )

        addresses = await app.user_db.execute_raw_select_query(address_select_query)
        return addresses
