from http import HTTPStatus
from quart import Blueprint, current_app as app
from quart_schema import validate_request, validate_querystring

from .constants import Roles
from .request_validation import (
    createMenu,
    fetchMenu,
    UpdateMenu,
)
from app.inventory_service.inventory_management import inventoryManager
from app.utils import send_api_response

BASE_ROUTE = "/inventory"

inventory_bp = Blueprint("inventory_service", __name__, url_prefix=BASE_ROUTE)
LOGGER_KEY = "app.inventory_service.routes"


@inventory_bp.route("/public/healthz", methods=["GET"])
async def health_check():
    """
    health api of user service to check if user service is working fine or not.
    """
    return {"message": "OK"}


@inventory_bp.route("/populate-menu", methods=["POST"])
@validate_request(createMenu)
async def create_menu(data: createMenu):
    app.logger.info(f"{LOGGER_KEY}.create_menu")

    payload = data.dict()
    role = payload.get("role")
    if role.value != Roles.RESTAURANT.value:
        return send_api_response(
            "Permission not granted to add food item to menu", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    inventory_manager = inventoryManager(payload)
    food_item_details = await inventory_manager.getFoodItem()
    if food_item_details.get("error"):
        return send_api_response(
            f"Unable to fetch food item details: {food_item_details.get('error')}",
            False,
            status_code=food_item_details.get("status_code"),
        )
    if food_item_details.get("food_item_id"):
        return send_api_response(
            "Food item already exists.",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    add_food_item_response = await inventory_manager.addFoodItem()
    if add_food_item_response.get("error"):
        return send_api_response(
            f"failed to add food item: {add_food_item_response.get('error')}",
            False,
            status_code=add_food_item_response.get("status_code"),
        )

    return send_api_response("Food item added successfully", True, HTTPStatus.OK.value)


@inventory_bp.route("/fetch-menu", methods=["GET"])
@validate_querystring(fetchMenu)
async def fetch_menu(query_args: fetchMenu):
    app.logger.info(f"{LOGGER_KEY}.fetch_menu")

    payload = query_args.dict()
    role = payload.get("role")
    if role.value == Roles.RIDER.value:
        return send_api_response(
            "Permission not granted to fetch the menu", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    inventory_manager = inventoryManager(payload)
    menu_response = await inventory_manager.getMenu()
    if menu_response.get("error"):
        return send_api_response(
            f"unable to fetch menu: {menu_response.get('error')}", False, status_code=menu_response.get("status_code")
        )

    return send_api_response(
        "fetched menu successfully", True, data=menu_response["menu"], status_code=HTTPStatus.OK.value
    )


@inventory_bp.route("/update-menu", methods=["PATCH"])
@validate_request(UpdateMenu)
async def update_menu(data: UpdateMenu):
    app.logger.info(f"{LOGGER_KEY}.update_menu")
    payload = data.dict()

    role = payload.get("role")
    if role.value == Roles.RIDER.value:
        return send_api_response(
            "Permission not granted to update the menu", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    inventory_manager = inventoryManager(payload)
    food_item_details = await inventory_manager.getFoodItem()
    if food_item_details.get("error"):
        return send_api_response(
            f"Unable to fetch food item details: {food_item_details.get('error')}",
            False,
            status_code=food_item_details.get("status_code"),
        )
    if not food_item_details.get("food_item_id"):
        return send_api_response(
            "Food item does not exists.",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    update_response = await inventory_manager.updateMenu()
    if update_response.get("error"):
        return send_api_response(
            f"failed to add food item: {update_response.get('error')}",
            False,
            status_code=update_response.get("status_code"),
        )

    return send_api_response("Menu updated successfully", True, HTTPStatus.OK.value)
