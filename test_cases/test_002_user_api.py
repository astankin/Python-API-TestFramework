import pytest
from utilities.get_token import get_auth_token
from utilities.helpers import generate_random_name, generate_random_password, generate_random_email, get_user_token
from utilities.json_validator import ResponseValidator
from utilities.logger import setup_logger
from utilities.read_config import ReadConfig
from utilities.request_handler import send_request
from utilities.fixtures import create_user

logger = setup_logger(log_file_path=ReadConfig.get_logs_users_path())

BASE_HEADERS = {"Content-Type": "application/json"}
USERS_ENDPOINT = ReadConfig.get_users_endpoint()
REGISTER_ENDPOINT = ReadConfig.get_register_user_endpoint()
EDIT_ENDPOINT = ReadConfig.get_edit_user_endpoint()
DELETE_ENDPOINT = ReadConfig.get_delete_user_endpoint()
ADMIN_TOKEN = get_auth_token()


def tear_down_user(user_id):
    headers = {"Content-Type": "application/json", "Authorization":f'Bearer {ADMIN_TOKEN}'}
    endpoint = f"{DELETE_ENDPOINT}{user_id}/"
    response = send_request(method="DELETE", endpoint=endpoint, headers=headers)
    assert response.status_code in [200, 204]

def test_get_users():
    headers = {**BASE_HEADERS, "Authorization": f'Bearer {ADMIN_TOKEN}'}
    response = send_request("GET", USERS_ENDPOINT, headers=headers, logger=logger)
    assert response.status_code == 200
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()

def test_get_user_by_id(create_user):
    user_id = create_user['id']
    headers = {**BASE_HEADERS, "Authorization": f'Bearer {ADMIN_TOKEN}'}
    response = send_request("GET", f"{USERS_ENDPOINT}/{user_id}", headers=headers, logger=logger)
    assert response.status_code == 200
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()

    expected_fields = {
        "_id": int,
        "username": str,
        "email": str,
        "name": str,
        "isAdmin": bool,
    }
    expected_values = {
        "_id": user_id,
        "username": create_user['email'],
        "email": create_user['email'],
        "name": create_user['name'],
        "isAdmin": False,
    }
    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)

def test_get_user_with_no_admin_token(create_user):
    user_id = create_user['id']
    headers = {"Authorization": ""}
    response = send_request("GET", f"{USERS_ENDPOINT}/{user_id}", headers=headers, logger=logger)
    assert response.status_code == 401
    validator = ResponseValidator(response, logger=logger)
    validator.validate_field_value({"detail": "Authentication credentials were not provided."})

def test_get_user_with_invalid_id():
    headers = {"Authorization": ADMIN_TOKEN}
    response = send_request("GET", f"{USERS_ENDPOINT}/invalid-id", headers=headers, logger=logger)
    assert response.status_code == 401

def test_create_user():
    name = generate_random_name()
    email = generate_random_email()
    password = generate_random_password()

    payload = {
        "name": name,
        "email": email,
        "password": password
    }

    response = send_request("POST", REGISTER_ENDPOINT, payload=payload, logger=logger)
    assert response.status_code == 200

    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    # validator.validate_response_time()

    # Field type checks
    expected_types = {
        "id": int,
        "name": str,
        "email": str,
        "username": str,
        "isAdmin": bool,
    }
    validator.validate_data_type(expected_types)

    # Field value checks
    expected_values = {
        "name": name,
        "email": email,
        "username": email,
        "isAdmin": False,
    }
    validator.validate_field_value(expected_values)

    # Cleanup
    user_id = response.json()['id']
    tear_down_user(user_id)


def test_create_user_with_duplicate_email(create_user):
    payload = {
        "name": "Duplicate", 
        "email": create_user['email'], 
        "password": "newpassword123"
        }
    response = send_request("POST", REGISTER_ENDPOINT, payload=payload, logger=logger)
    assert response.status_code == 400
    data = response.json()
    assert data['detail'] == "User with this email already exists"

def test_create_user_with_invalid_email():
    payload = {
        "name": "Invalid Email", 
        "email": generate_random_name(), 
        "password": "password123"
        }
    response = send_request("POST", REGISTER_ENDPOINT, payload=payload, logger=logger)
    data = response.json()
    assert response.status_code == 400
    assert "email" in data

def test_edit_user_with_valid_data(create_user):
    user_token = get_user_token(username=create_user['email'], password=create_user['password'])
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {user_token}"
        }
    edited_name = "User Python Edited"
    payload = {
        "name": edited_name, 
        "email": create_user['email'], 
        "password": ""
        }
    response = send_request("PUT", EDIT_ENDPOINT, headers=headers, payload=payload, logger=logger)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == edited_name
    assert data["username"] == create_user['email']
    assert data["email"] == create_user['email']
    
    tear_down_user(create_user['id'])

def test_edit_user_with_invalid_data(create_user):
    user_token = get_user_token(username=create_user['email'], password=create_user['password'])
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"name": ""}
    response = send_request("PUT", EDIT_ENDPOINT, headers=headers, payload=payload, logger=logger)
    assert response.status_code == 500
    
    tear_down_user(create_user['id'])

def test_delete_user(create_user):
    user_id = create_user['id']
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    endpoint = f"{DELETE_ENDPOINT}{user_id}/"

    response = send_request("DELETE", endpoint, headers=headers, logger=logger)
    
    # Status code validation
    assert response.status_code in [200, 204]

    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()

    # If the server returns a message, check it
    if response.status_code == 200:
        assert response.json() == "User was deleted"


def test_delete_non_existent_user():
    user_id = 99999
    headers = {"Authorization": ADMIN_TOKEN}
    endpoint = f"{DELETE_ENDPOINT}{user_id}/"

    response = send_request("DELETE", endpoint, headers=headers, logger=logger)

    # Validate status code
    assert response.status_code == 401

    # Validate response headers and time
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()

    # Validate error message
    expected_error = {"detail": "Authentication credentials were not provided."}
    validator.validate_field_value(expected_error)

