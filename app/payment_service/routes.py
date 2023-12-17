from http import HTTPStatus
from quart import Blueprint, current_app as app

from app.utils import send_api_response

BASE_ROUTE = "/payment"

payment_bp = Blueprint("payment_service", __name__, url_prefix=BASE_ROUTE)
LOGGER_KEY = "app.payment_service.routes"


@payment_bp.route("/public/health", methods=["GET"])
async def health_check():
    """
    health api of payment service to check if user service is working fine or not.
    """
    return {"message": "OK"}


@payment_bp.route("/process", methods=["POST"])
async def process_payment():
    app.logger.info(f"{LOGGER_KEY}.process_payment")

    return send_api_response("payment successful", True, status_code=HTTPStatus.OK.value)
