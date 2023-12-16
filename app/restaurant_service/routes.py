from http import HTTPStatus
from quart import Blueprint, current_app as app
from quart_schema import validate_request, validate_querystring

from .constants import Roles
from .request_validation import (
    createMenu,
    fetchMenu,
    UpdateMenu,
    Search,
    UpdateAvailabilty,
)
from app.restaurant_service.restaurant_management import restaurantManager
from app.utils import send_api_response

BASE_ROUTE = "/restaurant"

restaurant_bp = Blueprint("restaurant_service", __name__, url_prefix=BASE_ROUTE)
LOGGER_KEY = "app.restaurant_service.routes"


@restaurant_bp.route("/public/healthz", methods=["GET"])
async def health_check():
    """
    health api of user service to check if user service is working fine or not.
    """
    return {"message": "OK"}


@restaurant_bp.route("/populate-menu", methods=["POST"])
@validate_request(createMenu)
async def create_menu(data: createMenu):
    app.logger.info(f"{LOGGER_KEY}.create_menu")

    payload = data.dict()
    role = payload.get("role")
    if role.value != Roles.RESTAURANT.value:
        return send_api_response(
            "Permission not granted to add food item to menu", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    restaurant_manager = restaurantManager(payload)
    food_item_details = await restaurant_manager.getFoodItem()
    if food_item_details.get("error"):
        return send_api_response(
            f"Unable to fetch food item details: {food_item_details.get('error')}",
            False,
            status_code=food_item_details.get("status_code"),
        )
    if food_item_details.get("data", []) and food_item_details.get("data", [])[0].get("food_item_id"):
        return send_api_response(
            "Food item already exists.",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    add_food_item_response = await restaurant_manager.addFoodItem()
    if add_food_item_response.get("error"):
        return send_api_response(
            f"failed to add food item: {add_food_item_response.get('error')}",
            False,
            status_code=add_food_item_response.get("status_code"),
        )

    return send_api_response("Food item added successfully", True, HTTPStatus.OK.value)


@restaurant_bp.route("/fetch-menu", methods=["GET"])
@validate_querystring(fetchMenu)
async def fetch_menu(query_args: fetchMenu):
    app.logger.info(f"{LOGGER_KEY}.fetch_menu")

    payload = query_args.dict()
    role = payload.get("role")
    if role.value == Roles.RIDER.value:
        return send_api_response(
            "Permission not granted to fetch the menu", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    restaurant_manager = restaurantManager(payload)
    menu_response = await restaurant_manager.getMenu()
    if menu_response.get("error"):
        return send_api_response(
            f"unable to fetch menu: {menu_response.get('error')}", False, status_code=menu_response.get("status_code")
        )

    return send_api_response(
        "fetched menu successfully", True, data=menu_response["menu"], status_code=HTTPStatus.OK.value
    )


@restaurant_bp.route("/update-menu", methods=["PATCH"])
@validate_request(UpdateMenu)
async def update_menu(data: UpdateMenu):
    app.logger.info(f"{LOGGER_KEY}.update_menu")
    payload = data.dict()

    role = payload.get("role")
    if role.value == Roles.RIDER.value:
        return send_api_response(
            "Permission not granted to update the menu", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    restaurant_manager = restaurantManager(payload)
    food_item_details = await restaurant_manager.getFoodItem()
    if food_item_details.get("error"):
        return send_api_response(
            f"Unable to fetch food item details: {food_item_details.get('error')}",
            False,
            status_code=food_item_details.get("status_code"),
        )
    if not food_item_details.get("data", []):
        return send_api_response(
            "Food item does not exists.",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    update_response = await restaurant_manager.updateMenu()
    if update_response.get("error"):
        return send_api_response(
            f"failed to add food item: {update_response.get('error')}",
            False,
            status_code=update_response.get("status_code"),
        )

    return send_api_response("Menu updated successfully", True, HTTPStatus.OK.value)


@restaurant_bp.route("/search/food-item", methods=["GET"])
@validate_querystring(Search)
async def food_item_search(query_args: Search):
    app.logger.info(f"{LOGGER_KEY}.food_item_search")
    payload = query_args.dict()

    role = payload.get("role")
    if role.value == Roles.RIDER.value:
        return send_api_response(
            "Permission not granted to fetch the menu", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    restaurant_manager = restaurantManager(payload)
    food_item_search_respone = await restaurant_manager.foodItemSearch()
    if food_item_search_respone.get("error"):
        return send_api_response(
            f"failed to search food item: {food_item_search_respone.get('error')}",
            False,
            status_code=food_item_search_respone.get("status_code"),
        )

    return send_api_response(
        "successfully searched the food item",
        True,
        data=food_item_search_respone.get("data"),
        status_code=HTTPStatus.OK.value,
    )


@restaurant_bp.route("/search", methods=["GET"])
@validate_querystring(Search)
async def restaurant_search(query_args: Search):
    app.logger.info(f"{LOGGER_KEY}.restaurant_search")
    payload = query_args.dict()

    role = payload.get("role")
    if role.value != Roles.CUSTOMER.value:
        return send_api_response(
            "Permission not granted to search the restaurant", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    restaurant_manager = restaurantManager(payload)
    food_item_search_respone = await restaurant_manager.restaurantSearch()
    if food_item_search_respone.get("error"):
        return send_api_response(
            f"failed to search restaurant: {food_item_search_respone.get('error')}",
            False,
            status_code=food_item_search_respone.get("status_code"),
        )

    return send_api_response(
        "successfully searched the restaurant",
        True,
        data=food_item_search_respone.get("data"),
        status_code=HTTPStatus.OK.value,
    )


@restaurant_bp.route("/update-availabilty", methods=["PATCH"])
@validate_request(UpdateAvailabilty)
async def update_availability(data: UpdateAvailabilty):
    app.logger.info(f"{LOGGER_KEY}.update_availability")
    payload = data.dict()

    role = payload.get("role")
    if role.value != Roles.RESTAURANT.value:
        return send_api_response(
            "Permission not granted to update the availabilty of restaurant",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    restaurant_manager = restaurantManager(payload)
    response = await restaurant_manager.updateAvailabilty()
    if response.get("error"):
        return send_api_response(
            f"update in updating the availabilty: {response['error']}", False, status_code=response.get("status_code")
        )

    return send_api_response("updated the availabilty", True, status_code=HTTPStatus.OK.value)
