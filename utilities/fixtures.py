import pytest

from utilities.get_token import get_auth_token
from utilities.helpers import generate_random_name, generate_random_email, generate_random_password
from utilities.read_config import ReadConfig
from utilities.request_handler import send_request



@pytest.fixture
def create_user():
    name = generate_random_name()
    email = generate_random_email()
    password = generate_random_password()
    payload = {
        "name": name,
        "email": email,
        "password": password
    }
    response = send_request("POST", ReadConfig.get_register_user_endpoint(), payload=payload)
    assert response.status_code == 200
    data = response.json()

    yield {
        "id": data["id"],
        "name": name,
        "email": email,
        "password": password
    }

    # Cleanup (teardown)
    admin_token = f"Bearer {get_auth_token()}"
    delete_headers = {
        "Content-Type": "application/json",
        "Authorization": admin_token
    }
    send_request("DELETE", f"{ReadConfig.get_delete_user_endpoint()}{data['id']}/", headers=delete_headers)