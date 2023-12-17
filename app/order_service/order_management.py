import json
import aiohttp
from uuid import uuid4
from http import HTTPStatus
from datetime import datetime
from quart import current_app as app

from app.order_service.constants import Roles, Tables, OrderStatus
from app.order_service.cart_management import cartManager
from app.settings import PAYMENT_SERVICE_BASE_URL, DELIVERY_SERVICE_BASE_URL

LOGGER_KEY = "app.order_service.order_management"


class orderManager:
    def __init__(self, kwargs) -> None:
        self.order_id = kwargs.get("order_id")
        self.customer_id = kwargs.get("customer_id")
        self.restaurant_id = kwargs.get("restaurant_id")
        self.rider_id = kwargs.get("rider_id")
        self.payment_info = kwargs.get("payment_info")
        self.order_status = kwargs.get("order_status")

    async def placeOrder(self):
        """
        ・orders the active cart
        ・pushes order details into DB
        ・triggers one event to delivery service to find delivery partner
        """
        app.logger.info(f"{LOGGER_KEY}.placeOrder")
        response = {"error": None}

        if not self.order_id:
            self.order_id = uuid4()

        try:
            cart_kwargs = {"customer_id": self.customer_id}
            cart_manager = cartManager(cart_kwargs)
            ordered_items = await cart_manager.getCartItems()
            if ordered_items.get("error"):
                return ordered_items
            ordered_items = ordered_items["data"]
            if not ordered_items:
                response["error"] = "Empty cart cannot be ordered"
                response["status_code"] = HTTPStatus.BAD_REQUEST.value
                return response

            payment_response = await self.processPayment()
            if payment_response.get("error"):
                return payment_response

            insert_response = await self.insertOrderDetails(ordered_items)
            if insert_response.get("error"):
                return insert_response

            checkout_cart_response = await cart_manager.checkOutCart()
            if checkout_cart_response.get("error"):
                return checkout_cart_response

            delivery_service_response = await self.pushTaskToDeliveryService()
            if delivery_service_response.get("error"):
                return delivery_service_response
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.placeOrder.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def processPayment(self):
        """
        calls payment service api to process the payment
        """
        app.logger.info(f"{LOGGER_KEY}.processPayment")
        response = {"error": None}

        try:
            url = f"{PAYMENT_SERVICE_BASE_URL.rstrip('/')}/process"
            payload = {"order_id": str(self.order_id), "payment_info": self.payment_info}

            async with aiohttp.ClientSession() as client:
                payment_response = await client.post(url=url, json=payload)
                status_code = payment_response.status
                response_text = await payment_response.text()
                response_text = json.loads(response_text)
                app.logger.info(f"{LOGGER_KEY}.processPayment.status_code: {status_code}")
                if status_code != HTTPStatus.OK.value:
                    app.logger.error(f"{LOGGER_KEY}.processPayment.error: {response_text}")
                    response["error"] = response_text["message"]
                    response["status_code"] = HTTPStatus.FAILED_DEPENDENCY.value
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.processPayment.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def insertOrderDetails(self, ordered_items):
        """
        pushes order details into DB
        """
        app.logger.info(f"{LOGGER_KEY}.insertOrderDetails")
        response = {"error": None}

        try:
            order_insert_query = self.getOrderInsertQuery()
            if order_insert_query.get("error"):
                return order_insert_query
            order_insert_query = order_insert_query["query"]

            ordered_items_insert_query = self.getOrderItemsInsertQuery(ordered_items)
            if ordered_items_insert_query.get("error"):
                return ordered_items_insert_query
            ordered_items_insert_query = ordered_items_insert_query["query"]

            transaction_query = f"BEGIN; {order_insert_query} {ordered_items_insert_query} COMMIT;"
            insert_response = await app.order_db.execute_raw_transaction_query(transaction_query)
            app.logger.info(f"{LOGGER_KEY}.insertOrderDetails.insert_response: {insert_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.insertOrderDetails.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    def getOrderInsertQuery(self):
        """
        returns orders table insert query
        """
        app.logger.info(f"{LOGGER_KEY}.getOrderInsertQuery")
        response = {"error": None}

        try:
            total_amount = self.payment_info.get("amount")
            order_status = OrderStatus.ORDER_PLACED.value
            columns = Tables.ORDERS.value["columns"]
            columns.remove("rider_id")
            columns.remove("delivery_time")
            columns.remove("cancelled_time")
            columns = ", ".join(columns)
            query = f"INSERT INTO {Tables.ORDERS.value['name']} ({columns}) VALUES ('{self.order_id}', '{self.customer_id}', '{self.restaurant_id}', '{total_amount}', '{order_status}');"
            response["query"] = query
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getOrderInsertQuery.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    def getOrderItemsInsertQuery(self, ordered_items):
        """
        returns order_items table insert query
        """
        app.logger.info(f"{LOGGER_KEY}.getOrderItemsInsertQuery")
        response = {"error": None}

        try:
            columns = ", ".join(Tables.ORDER_ITEMS.value["columns"])
            query = f"INSERT INTO {Tables.ORDER_ITEMS.value['name']} ({columns}) VALUES "
            for ordered_item in ordered_items:
                query += f"('{self.order_id}', '{ordered_item['food_item_id']}', '{ordered_item['quantity']}', '{ordered_item['price']}'), "
            query = f"{query.strip(', ') } ;"
            response["query"] = query
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getOrderItemsInsertQuery.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def pushTaskToDeliveryService(self):
        """
        triggers one event to delivery service to find delivery partner
        """
        app.logger.info(f"{LOGGER_KEY}.pushTaskToDeliveryService")
        response = {"error": None}

        try:
            url = f"{DELIVERY_SERVICE_BASE_URL}/assign-delivery-partner"
            payload = {
                "order_id": str(self.order_id),
                "customer_id": self.customer_id,
                "restaurant_id": self.restaurant_id,
            }

            async with aiohttp.ClientSession() as client:
                payment_response = await client.post(url=url, json=payload)
                status_code = payment_response.status
                response_text = await payment_response.text()
                response_text = json.loads(response_text)
                app.logger.info(f"{LOGGER_KEY}.pushTaskToDeliveryService.status_code: {status_code}")
                if status_code != HTTPStatus.OK.value:
                    app.logger.error(f"{LOGGER_KEY}.pushTaskToDeliveryService.error: {response_text}")
                    response["error"] = response_text["message"]
                    response["status_code"] = HTTPStatus.FAILED_DEPENDENCY.value
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.pushTaskToDeliveryService.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def updateOrder(self):
        """
        update order_status according to respective user type
        """
        app.logger.info(f"{LOGGER_KEY}.updateOrder")
        response = {"error": None}

        try:
            query = f"UPDATE {Tables.ORDERS.value['name']} SET order_status = '{self.order_status.value}', updated_at = '{str(datetime.now())}' where order_id = '{self.order_id}';"
            update_response = await app.order_db.execute_insert_or_update_query(query)
            app.logger.info(f"{LOGGER_KEY}.updateOrder.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.updateOrder.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def getOrders(self, role):
        """
        fetches the Orders from DB of a user
        ・ordered by a customer
        ・prepared by a restaurant
        ・delivered by a rider
        """
        app.logger.info(f"{LOGGER_KEY}.getOrders")
        response = {"error": None}

        try:
            columns = ", ".join(Tables.ORDERS.value["columns"])
            query = f"SELECT {columns} FROM {Tables.ORDERS.value['name']} WHERE "
            if role.value == Roles.CUSTOMER.value:
                query += f"customer_id = '{self.customer_id}' ORDER BY created_at DESC;"
            if role.value == Roles.RESTAURANT.value:
                query += f"restaurant_id = '{self.restaurant_id}' ORDER BY created_at DESC;"
            if role.value == Roles.RIDER.value:
                query += f"rider_id = '{self.rider_id}' ORDER BY created_at DESC;"
            order_history = await app.order_db.execute_raw_select_query(query)
            response["data"] = order_history
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.getOrders.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response

    async def updateRider(self):
        """
        updates the delivery partner's id in order table
        """
        app.logger.info(f"{LOGGER_KEY}.updateRider")
        response = {"error": None}

        try:
            query = f"UPDATE {Tables.ORDERS.value['name']} SET rider_id = '{self.rider_id}' WHERE order_id = '{self.order_id}';"
            update_response = await app.order_db.execute_insert_or_update_query(query)
            app.logger.info(f"{LOGGER_KEY}.updateRider.update_response: {update_response}")
        except Exception as e:
            app.logger.error(f"{LOGGER_KEY}.updateRider.exception: {str(e)}")
            response["error"] = str(e)
            response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
        return response
