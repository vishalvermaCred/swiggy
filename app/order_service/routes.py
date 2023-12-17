from http import HTTPStatus
from quart import Blueprint, current_app as app
from quart_schema import validate_request, validate_querystring

from .request_validation import (
    PlaceOrder,
    UpdateOrder,
    UpdateRider,
    OrderHistory,
    GetCartTotal,
    AddItemToCart,
    DeleteItemFromCart,
)
from app.order_service.cart_management import cartManager
from app.order_service.order_management import orderManager
from app.utils import send_api_response

BASE_ROUTE = "/order"

order_bp = Blueprint("order_service", __name__, url_prefix=BASE_ROUTE)
LOGGER_KEY = "app.order_service.routes"


@order_bp.route("/public/health", methods=["GET"])
async def health_check():
    """
    health api of order service to check if user service is working fine or not.
    """
    return {"message": "OK"}


@order_bp.route("/add-item-to-cart", methods=["POST"])
@validate_request(AddItemToCart)
async def add_item_to_cart(data: AddItemToCart):
    app.logger.info(f"{LOGGER_KEY}.add_item_to_cart")
    payload = data.dict()

    cart_manager = cartManager(payload)
    cart_items = await cart_manager.getCartItems()
    if cart_items.get("error"):
        return send_api_response(
            f"failed to fetch cart: {cart_items['error']}", False, status_code=cart_items["status_code"]
        )
    cart_items = cart_items["data"]
    cart_items = next(
        (cart_item for cart_item in cart_items if str(cart_item["food_item_id"]) == payload["food_item_id"]), None
    )
    if cart_items:
        if not cart_manager.isFoodItemFromSameRestaurant(cart_items):
            print(f"\n\n here \n\n")
            return send_api_response(
                f"Your cart contains items from diff restaurant", False, status_code=HTTPStatus.BAD_REQUEST.value
            )

    if not cart_items:
        response = await cart_manager.insertItemToCart()
        if response.get("error"):
            return send_api_response(
                f"failed to add item to the cart: {response['error']}", False, status_code=response["status_code"]
            )
    else:
        print(f"\n\n cart_items: {cart_items} \n\n")
        cart_manager.id = cart_items["id"]
        response = await cart_manager.addItemToCart()
        if response.get("error"):
            return send_api_response(
                f"failed to add item to the cart: {response['error']}", False, status_code=response["status_code"]
            )

    return send_api_response("item added to the cart", True, status_code=HTTPStatus.OK.value)


@order_bp.route("/delete-item-from-cart", methods=["POST"])
@validate_request(DeleteItemFromCart)
async def delete_item_from_cart(data: DeleteItemFromCart):
    app.logger.info(f"{LOGGER_KEY}.delete_item_from_cart")
    payload = data.dict()

    cart_manager = cartManager(payload)
    cart_items = await cart_manager.getCartItems()
    if cart_items.get("error"):
        return send_api_response(
            f"failed to fetch cart: {cart_items['error']}", False, status_code=cart_items["status_code"]
        )
    cart_items = cart_items["data"]
    if not cart_items:
        return send_api_response(f"Your cart is empty", False, status_code=HTTPStatus.BAD_REQUEST.value)
    else:
        cart_items = next(
            (cart_item for cart_item in cart_items if str(cart_item["food_item_id"]) == payload["food_item_id"]), None
        )
        if not cart_items:
            return send_api_response(f"food item not in cart", False, status_code=HTTPStatus.BAD_REQUEST.value)

        cart_manager.id = cart_items["id"]
        response = await cart_manager.deleteItemFromCart()
        if response.get("error"):
            return send_api_response(
                f"failed to delete item from the cart: {response['error']}", False, status_code=response["status_code"]
            )

    return send_api_response("item deleted from the cart", True, status_code=HTTPStatus.OK.value)


@order_bp.route("/get-cart-total", methods=["GET"])
@validate_querystring(GetCartTotal)
async def get_cart_total(query_args: GetCartTotal):
    app.logger.info(f"{LOGGER_KEY}.get_cart_total")
    payload = query_args.dict()

    cart_manager = cartManager(payload)
    response = await cart_manager.getCartTotal()
    if response.get("error"):
        return send_api_response(
            f"Failed to get cart total: {response['error']}", False, status_code=response["status_code"]
        )

    return send_api_response(
        "Cart total fetched successfully", True, data=response["cart_total"], status_code=HTTPStatus.OK.value
    )


# place order
@order_bp.route("/place-order", methods=["POST"])
@validate_request(PlaceOrder)
async def place_order(data: PlaceOrder):
    app.logger.info(f"{LOGGER_KEY}.place_order")
    payload = data.dict()

    order_manager = orderManager(payload)
    response = await order_manager.placeOrder()
    if response.get("error"):
        return send_api_response(
            f"failed to process the order: {response['error']}", False, status_code=response["status_code"]
        )

    return send_api_response("Order placed successfully", True, status_code=HTTPStatus.OK.value)


@order_bp.route("/update-order", methods=["PATCH"])
@validate_request(UpdateOrder)
async def update_order(data: UpdateOrder):
    app.logger.info(f"{LOGGER_KEY}.update_order")
    payload = data.dict()

    order_manager = orderManager(payload)
    response = await order_manager.updateOrder()
    if response.get("error"):
        return send_api_response(
            f"failed to update the order: {response['error']}", False, status_code=response["status_code"]
        )

    return send_api_response("Order updated successfully", True, status_code=HTTPStatus.OK.value)


@order_bp.route("/history", methods=["GET"])
@validate_querystring(OrderHistory)
async def order_history(query_args: OrderHistory):
    app.logger.info(f"{LOGGER_KEY}.order_history")
    payload = query_args.dict()

    role = payload.get("role")
    order_manager = orderManager(payload)
    response = await order_manager.getOrders(role)
    if response.get("error"):
        return send_api_response(
            f"failed to fetch the orders: {response['error']}", False, status_code=response["status_code"]
        )

    return send_api_response(
        "Order history fetched successfully", True, data=response["data"], status_code=HTTPStatus.OK.value
    )


@order_bp.route("/update-rider", methods=["PATCH"])
@validate_request(UpdateRider)
async def update_rider(data: UpdateRider):
    app.logger.info(f"{LOGGER_KEY}.update_rider")
    payload = data.dict()

    order_manager = orderManager(payload)
    response = await order_manager.updateRider()
    if response.get("error"):
        return send_api_response(
            f"failed to fetch the orders: {response['error']}", False, status_code=response["status_code"]
        )

    return send_api_response("Rider updated successfully", True, status_code=HTTPStatus.OK.value)
