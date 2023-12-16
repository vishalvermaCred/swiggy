from uuid import uuid4
from http import HTTPStatus
from quart import current_app as app

from .constants import Tables
from .filters.price import Price
from .filters.rating import Rating
from .filters.cuisine import Cuisine
from .filters.meal_type import mealType

LOGGER_KEY = "app.restaurant_service.restaurant_management"


class restaurantManager:
    def __init__(self, kwargs) -> None:
        self.food_item_id = kwargs.get("food_item_id")
        self.restaurant_id = kwargs.get("restaurant_id")
        self.food_item_name = kwargs.get("food_item_name", "")
        self.restaurant_name = kwargs.get("restaurant_name", "")
        self.description = kwargs.get("description")
        self.meal_type = kwargs.get("meal_type")
        self.cuisine_type = kwargs.get("cuisine_type")
        self.price = kwargs.get("price")
        self.stock_quantity = kwargs.get("stock_quantity")
        self.ordered_quantity = kwargs.get("ordered_quantity")
        self.restock_quantity = kwargs.get("restock_quantity")
        self.price_range = kwargs.get("price_range")
        self.rating = kwargs.get("rating")
        self.is_available = kwargs.get("is_available")

    async def getFoodItem(self):
        app.logger.info(f"{LOGGER_KEY}.getFoodItem")
        response = {"error": None}

        try:
            if not (self.food_item_id or self.food_item_name or self.restaurant_id):
                response["error"] = "food item details not provided"
                response["status_code"] = HTTPStatus.BAD_REQUEST.value

            columns = ", ".join(Tables.MENU.value["columns"])
            select_query = f"SELECT {columns} FROM {Tables.MENU.value['name']} where "
            if self.food_item_id:
                select_query += f"food_item_id = '{self.food_item_id}' and "
            if self.food_item_name:
                select_query += f"name like '%{self.food_item_name.lower()}%' and "
            if self.restaurant_id:
                select_query += f"restaurant_id = '{self.restaurant_id}' and "

            select_query += "is_available = true;"

            food_item_details = await app.restaurant_db.execute_raw_select_query(select_query)
            response["data"] = food_item_details
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
            insert_query = f"INSERT INTO {Tables.MENU.value['name']} ({columns}) VALUES ('{self.food_item_id}', '{self.restaurant_id}', '{self.food_item_name}', '{self.price}', '{self.stock_quantity}', "
            insert_query += f"'{self.meal_type.value}', " if self.meal_type else f"null, "
            insert_query += f"'{self.cuisine_type}', " if self.cuisine_type else f"null, "
            insert_query += f"'{self.description}', " if self.description else f"null, "
            insert_query = f"{insert_query.strip(', ')} );"

            insert_response = await app.restaurant_db.execute_insert_or_update_query(insert_query)
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

            menu = await app.restaurant_db.execute_raw_select_query(select_query)
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
            if self.food_item_name:
                update_clause += f"name = '{self.food_item_name}', "
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
            update_response = await app.restaurant_db.execute_insert_or_update_query(update_query)
            app.logger.info(f"{LOGGER_KEY}.updateMenu.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.updateMenu.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value

        return response

    async def foodItemSearch(self):
        app.logger.info(f"{LOGGER_KEY}.foodItemSearch")
        response = {"error": None}
        filters = []

        if self.price_range:
            price_filter = Price(self.price_range)
            filters.append(price_filter)

        if self.cuisine_type:
            cuisine_filter = Cuisine(self.cuisine_type)
            filters.append(cuisine_filter)

        if self.meal_type:
            meal_type_filter = mealType(self.meal_type)
            filters.append(meal_type_filter)

        if self.rating:
            rating_filter = Rating(self.rating)
            filters.append(rating_filter)

        food_items = await self.getFoodItem()
        if food_items.get("error"):
            return food_items

        food_items = food_items["data"]
        food_items = await self.getFilteredData(filters, food_items)
        response["data"] = food_items
        return response

    async def getFilteredData(self, filters, food_items):
        app.logger.info(f"{LOGGER_KEY}.getFilteredData")

        if not filters:
            return food_items

        for filter in filters:
            filtered_food_items = []
            for food_item in food_items:
                if filter.filter(food_item):
                    filtered_food_items.append(food_item)
            food_items = filtered_food_items

        return food_items

    async def restaurantSearch(self):
        app.logger.info(f"{LOGGER_KEY}.restaurantSearch")
        response = {"error": None}
        filters = []

        if self.cuisine_type:
            cuisine_filter = Cuisine(self.cuisine_type)
            filters.append(cuisine_filter)

        if self.meal_type:
            meal_type_filter = mealType(self.meal_type)
            filters.append(meal_type_filter)

        if self.rating:
            rating_filter = Rating(self.rating)
            filters.append(rating_filter)

        restaurant_data = await self.getRestaurant()
        if restaurant_data.get("error"):
            return restaurant_data

        restaurant_data = restaurant_data["data"]
        restaurant_data = await self.getFilteredData(filters, restaurant_data)
        response["data"] = restaurant_data
        return response

    async def getRestaurant(self):
        app.logger.info(f"{LOGGER_KEY}.getRestaurant")
        response = {"error": None}

        try:
            if not self.restaurant_name:
                response["error"] = "restaurant name not found"
                response["status_code"] = HTTPStatus.BAD_REQUEST.value

            columns = ", ".join(Tables.RESTAURANT.value["columns"])
            select_query = f"SELECT {columns} FROM {Tables.RESTAURANT.value['name']} where "
            if self.restaurant_id:
                select_query += f"user_id = '{self.restaurant_id}' and "
            if self.restaurant_name:
                select_query += f"name like '%{self.restaurant_name.lower()}%' and "
            select_query += "is_available = true; "

            restaurant_details = await app.user_db.execute_raw_select_query(select_query)
            response["data"] = restaurant_details
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getRestaurant.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def updateAvailability(self):
        app.logger.info(f"{LOGGER_KEY}.updateAvailability")
        response = {"error": None}

        try:
            update_query = f"UPDATE {Tables.RESTAURANT.value['name']} SET is_available = '{self.is_available}' where user_id = '{self.restaurant_id}';"

            update_response = await app.user_db.execute_insert_or_update_query(update_query)
            app.logger.info(f"{LOGGER_KEY}.updateAvailability.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.updateAvailability.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response
