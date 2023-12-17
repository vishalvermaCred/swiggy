from http import HTTPStatus
from quart import current_app as app

from app.order_service.constants import Tables

LOGGER_KEY = "app.order_service.cart_management"


class cartManager:
    def __init__(self, kwargs) -> None:
        self.id = kwargs.get("id")
        self.food_item_id = kwargs.get("food_item_id")
        self.restaurant_id = kwargs.get("restaurant_id")
        self.customer_id = kwargs.get("customer_id")
        self.role = kwargs.get("role")
        self.price = kwargs.get("price", 0)
        self.quantity = kwargs.get("quantity", 0)
        self.is_expired = kwargs.get("is_expired")

    async def getCartItems(self):
        app.logger.info(f"{LOGGER_KEY}.getCartItems")
        response = {"error": None}

        try:
            columns = ", ".join(Tables.CART.value["columns"])
            select_query = f"SELECT {columns} FROM {Tables.CART.value['name']} where customer_id='{self.customer_id}' and is_expired=false;"
            print(f"\n\n select_query: {select_query} \n\n")
            cart_item = await app.order_db.execute_raw_select_query(select_query)
            response["data"] = cart_item
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getCartItems.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def insertItemToCart(self):
        app.logger.info(f"{LOGGER_KEY}.insertItemToCart")
        response = {"error": None}

        try:
            columns = Tables.CART.value["columns"].copy()
            columns.remove("id")
            columns.remove("is_expired")
            columns = ", ".join(columns)
            insert_query = f"INSERT INTO {Tables.CART.value['name']} ({columns}) VALUES ('{self.food_item_id}', '{self.restaurant_id}', '{self.customer_id}', '{self.price}', 1);"
            insert_response = await app.order_db.execute_insert_or_update_query(insert_query)
            app.logger.info(f"{LOGGER_KEY}.insertItemToCart.insert_response: {insert_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.insertItemToCart.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    def isFoodItemFromSameRestaurant(self, cart_item):
        app.logger.info(f"{LOGGER_KEY}.isFoodItemFromSameRestaurant")
        return self.restaurant_id == str(cart_item["restaurant_id"])

    async def addItemToCart(self):
        app.logger.info(f"{LOGGER_KEY}.addItemToCart")
        response = {"error": None}

        try:
            update_query = f"UPDATE {Tables.CART.value['name']} SET quantity = quantity+1 WHERE id = '{self.id}';"
            update_response = await app.order_db.execute_insert_or_update_query(update_query)
            app.logger.info(f"{LOGGER_KEY}.addItemToCart.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.addItemToCart.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def deleteItemFromCart(self):
        app.logger.info(f"{LOGGER_KEY}.deleteItemFromCart")
        response = {"error": None}

        try:
            update_query = f"UPDATE {Tables.CART.value['name']} SET quantity = quantity-1, is_expired = (quantity-1)<=0 WHERE id = '{self.id}';"
            update_response = await app.order_db.execute_insert_or_update_query(update_query)
            app.logger.info(f"{LOGGER_KEY}.deleteItemFromCart.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.deleteItemFromCart.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def getCartTotal(self):
        app.logger.info(f"{LOGGER_KEY}.getCartTotal")
        response = {"error": None}

        try:
            cart = await self.getCartItems()
            if cart.get("error"):
                return cart

            cart = cart["data"]
            cart_total = 0
            for cart_item in cart:
                cart_total += cart_item.get("quantity") * cart_item.get("price")
            response["cart_total"] = cart_total
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getCartTotal.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def checkOutCart(self):
        app.logger.info(f"{LOGGER_KEY}.checkOutCart")
        response = {"error": None}

        try:
            update_query = f"UPDATE {Tables.CART.value['name']} SET is_expired = true WHERE customer_id='{self.customer_id}' and is_expired=false;"
            update_response = await app.order_db.execute_insert_or_update_query(update_query)
            app.logger.info(f"{LOGGER_KEY}.checkOutCart.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.checkOutCart.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response
