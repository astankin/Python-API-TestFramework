from venv import logger
from utilities.read_config import ReadConfig
from utilities.request_handler import send_request


def get_auth_token():
    login_payload = {
        "username": ReadConfig.get_admin_username(),
        "password": ReadConfig.get_admin_password()
    }
    response = send_request(
        method="POST",
        endpoint="users/login/",
        headers={"Content-Type": "application/json"},
        payload=login_payload,
        logger=logger
    )
    token = response.json().get("token")
    return token
