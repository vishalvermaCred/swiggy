from http import HTTPStatus
from quart import Blueprint, current_app as app
from quart_schema import validate_request, validate_querystring

from .constants import Roles
from app.user_service.request_validation import (
    userSignUp,
    CustomerSignIn,
    AddAddresses,
    FetchUser,
)
from app.user_service.user_management import userManager
from app.utils import send_api_response

BASE_ROUTE = "/user"

user_bp = Blueprint("user_service", __name__, url_prefix=BASE_ROUTE)
LOGGER_KEY = "app.user_service.routes"


@user_bp.route("/public/healthz", methods=["GET"])
async def health_check():
    """
    health api of user service to check if user service is working fine or not.
    """
    return {"message": "OK"}


@user_bp.route("/signup", methods=["POST"])
@validate_request(userSignUp)
async def user_sign_up(data: userSignUp):
    app.logger.info(f"{LOGGER_KEY}.user_sign_up")
    payload = data.dict()
    user_manager = userManager(payload)

    user_details = await user_manager.getUser()
    if user_details.get("error"):
        return send_api_response(
            f"Unable to fetch user: {user_details.get('error')}", False, status_code=user_details.get("status_code")
        )
    if user_details.get("user_id"):
        return send_api_response(
            "User already exists. Please sign in.",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    create_user_response = await user_manager.createUser()
    if create_user_response.get("error"):
        return send_api_response(
            f"user signup failed: {create_user_response.get('error')}",
            False,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        )

    return send_api_response("user signup successfull", True, HTTPStatus.OK.value)


@user_bp.route("/signin", methods=["GET"])
@validate_querystring(CustomerSignIn)
async def customer_sign_in(query_args: CustomerSignIn):
    app.logger.info(f"{LOGGER_KEY}.user_sign_in")
    payload = query_args.dict()
    user_manager = userManager(payload)

    response = await user_manager.getUser(fetch_user_with_address=True)
    if response.get("error"):
        return send_api_response(
            f"user signin failed: {response.get('error')}", False, status_code=response.get("status_code")
        )
    if not response.get("user_id"):
        return send_api_response(
            f"user does not exist. Please sign up", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    return send_api_response("user signin successfull", True, data=response, status_code=HTTPStatus.OK.value)


@user_bp.route("/fetch-user", methods=["GET"])
@validate_querystring(FetchUser)
async def fetch_user(query_args: FetchUser):
    app.logger.info(f"{LOGGER_KEY}.fetch_user")
    payload = query_args.dict()
    user_manager = userManager(payload)

    response = await user_manager.getUser(fetch_user_with_address=True)
    if response.get("error"):
        return send_api_response(
            f"failed to fetch user: {response.get('error')}", False, status_code=response.get("status_code")
        )

    return send_api_response("fetched user successfully", True, data=response, status_code=HTTPStatus.OK.value)


@user_bp.route("/add-addresses", methods=["POST"])
@validate_request(AddAddresses)
async def add_addresses(data: AddAddresses):
    app.logger.info(f"{LOGGER_KEY}.add_addresses")
    payload = data.dict()

    if payload.get("role") != Roles.CUSTOMER.value:
        return send_api_response(
            "only customer can have multiple addresses", False, status_code=HTTPStatus.BAD_REQUEST.value
        )

    user_manager = userManager(payload)
    user_details = await user_manager.getUser()
    if not user_details:
        return send_api_response(
            "User does not exists",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    if user_details.get("error"):
        return send_api_response(
            f"error in fetching user: {user_details.get('error')}", False, status_code=user_details.get("status_code")
        )

    add_addresses_response = await user_manager.insert_address()
    if add_addresses_response.get("error"):
        return send_api_response(
            f"error in inserting address: {add_addresses_response.get('error')}",
            False,
            status_code=add_addresses_response.get("status_code"),
        )

    return send_api_response("Address inserted successfully", True, status_code=HTTPStatus.OK.value)
