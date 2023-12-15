from uuid import uuid4
from http import HTTPStatus
from quart import current_app as app

from .constants import Tables

LOGGER_KEY = "app.inventory_service.inventory_management"


class inventoryManager:
    def __init__(self, kwargs) -> None:
        self.food_item_id = kwargs.get("food_item_id")
        self.restaurant_id = kwargs.get("restaurant_id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.meal_type = kwargs.get("meal_type")
        self.cuisine_type = kwargs.get("cuisine_type")
        self.price = kwargs.get("price")
        self.stock_quantity = kwargs.get("stock_quantity")
        self.ordered_quantity = kwargs.get("ordered_quantity")
        self.restock_quantity = kwargs.get("restock_quantity")

    async def getFoodItem(self):
        app.logger.info(f"{LOGGER_KEY}.getFoodItem")
        response = {"error": None}

        try:
            if not (self.food_item_id or (self.name and self.restaurant_id)):
                response["error"] = "food item details not provided"
                response["status_code"] = HTTPStatus.BAD_REQUEST.value

            columns = ", ".join(Tables.MENU.value["columns"])
            select_query = f"SELECT {columns} FROM {Tables.MENU.value['name']} where "
            if self.food_item_id:
                select_query += f"food_item_id = '{self.food_item_id}';"
            elif self.name and self.restaurant_id:
                select_query += f"name = '{self.name}' and restaurant_id = '{self.restaurant_id}';"

            food_item_details = await app.inventory_db.execute_raw_select_query(select_query)
            if food_item_details:
                food_item_details = food_item_details[0]
            else:
                food_item_details = {}
            response = food_item_details
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getFoodItem.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def addFoodItem(self):
        app.logger.info(f"{LOGGER_KEY}.addFoodItem")
        response = {"error": None}

        try:
            if not self.food_item_id:
                self.food_item_id = uuid4()

            columns = Tables.MENU.value["columns"]
            columns.remove("rating")
            columns.remove("is_available")
            columns = ", ".join(columns)

            # preparing insert query
            insert_query = f"INSERT INTO {Tables.MENU.value['name']} ({columns}) VALUES ('{self.food_item_id}', '{self.restaurant_id}', '{self.name}', '{self.price}', '{self.stock_quantity}', "
            insert_query += f"'{self.meal_type.value}', " if self.meal_type else f"null, "
            insert_query += f"'{self.cuisine_type}', " if self.cuisine_type else f"null, "
            insert_query += f"'{self.description}', " if self.description else f"null, "
            insert_query = f"{insert_query.strip(', ')} );"

            insert_response = await app.inventory_db.execute_insert_or_update_query(insert_query)
            app.logger.info(f"{LOGGER_KEY}.addFoodItem.insert_response: {insert_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.addFoodItem.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value

        return response

    async def getMenu(self):
        app.logger.info(f"{LOGGER_KEY}.getMenu")
        response = {"error": None}

        try:
            columns = ", ".join(Tables.MENU.value["columns"])
            select_query = f"SELECT {columns} FROM {Tables.MENU.value['name']} where restaurant_id = '{self.restaurant_id}' and is_available = true;"

            menu = await app.inventory_db.execute_raw_select_query(select_query)
            response["menu"] = menu
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getMenu.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value

        return response

    async def updateMenu(self):
        app.logger.info(f"{LOGGER_KEY}.updateMenu")
        response = {"error": None}

        try:
            update_query = f"UPDATE {Tables.MENU.value['name']} SET "
            update_clause = ""
            if self.name:
                update_clause += f"name = '{self.name}', "
            if self.description:
                update_clause += f"description = '{self.description}', "
            if self.price:
                update_clause += f"price = '{self.price}', "
            if self.ordered_quantity:
                update_clause += f"stock_quantity = stock_quantity-{self.ordered_quantity}, is_available = (stock_quantity-{self.ordered_quantity})>0, "
            if self.restock_quantity:
                update_clause += f"stock_quantity = stock_quantity+{self.restock_quantity}, is_available = (stock_quantity+{self.restock_quantity})>0, "

            update_clause = update_clause.strip(", ")
            update_query += update_clause + f" WHERE food_item_id = '{self.food_item_id}';"
            if not update_clause:
                response = {"error": "No data provided to be updated", "status_code": HTTPStatus.BAD_REQUEST.value}
            update_response = await app.inventory_db.execute_insert_or_update_query(update_query)
            app.logger.info(f"{LOGGER_KEY}.updateMenu.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.updateMenu.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value

        return response
