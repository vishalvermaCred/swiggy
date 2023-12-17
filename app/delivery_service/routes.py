from http import HTTPStatus
from quart import Blueprint, current_app as app

from app.utils import send_api_response

BASE_ROUTE = "/delivery"

delivery_bp = Blueprint("delivery_service", __name__, url_prefix=BASE_ROUTE)
LOGGER_KEY = "app.delivery_service.routes"


@delivery_bp.route("/public/health", methods=["GET"])
async def health_check():
    """
    health api of delivery service to check if user service is working fine or not.
    """
    return {"message": "OK"}


@delivery_bp.route("/assign-delivery-partner", methods=["POST"])
async def assign_delivery_partner():
    app.logger.info(f"{LOGGER_KEY}.assign_delivery_partner")
    """
    API to assign the delivery agent finding task to message queue
    """

    # TODO - assign the finding delivery partner to message queue

    return send_api_response("Looking for delivery partner", True, status_code=HTTPStatus.OK.value)
