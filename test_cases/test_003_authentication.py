import pytest
from utilities.delete_users_database import delete_user_by_id
from utilities.helpers import generate_random_password
from utilities.json_validator import ResponseValidator
from utilities.logger import setup_logger
from utilities.read_config import ReadConfig
from utilities.request_handler import send_request
from utilities.fixtures import create_user
from utilities.schema_loader import load_json_schema

# Setup shared constants and config
logger = setup_logger(log_file_path=ReadConfig.get_logs_authentication_path())
test_user_id = int(ReadConfig.get_tes_user_id())
test_user_name = ReadConfig.get_tes_user_name()
test_user_username = ReadConfig.get_tes_user_username()
test_user_email = ReadConfig.get_tes_user_email()
test_user_password = ReadConfig.get_tes_user_password()
login_endpoint = ReadConfig.get_login_endpoint()
login_schema = load_json_schema("login_schema.json")
headers = {"Content-Type": "application/json"}


def test_login_with_valid_credentials(create_user):
    payload = {
        "username": test_user_username,
        "password": test_user_password,
    }
    expected_fields = {
        "refresh": str,
        "access": str,
        "id": int,
        "_id": int,
        "username": str,
        "email": str,
        "name": str,
        "isAdmin": bool,
        "token": str,
    }
    expected_values = {
        "id": test_user_id,
        "_id": test_user_id,
        "username": test_user_username,
        "email": test_user_email,
        "name": test_user_name,
        "isAdmin": False,
    }

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 200
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)
    validator.validate_json_schema(login_schema)


def test_login_with_invalid_username():
    payload = {
        "username": "invalid_user", 
        "password": test_user_password
        }
    expected_error = {"detail": "No active account found with the given credentials"}

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 401
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_field_value(expected_error)


def test_login_with_invalid_password():
    payload = {
        "username": test_user_username, 
        "password": "InvalidPassword123@"
        }
    expected_error = {"detail": "No active account found with the given credentials"}

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 401
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    # validator.validate_response_time()
    validator.validate_field_value(expected_error)


def test_login_with_empty_username():
    payload = {
        "username": "", 
        "password": test_user_password
        }
    expected_fields = {"username": list}
    expected_values = {"username": ["This field may not be blank."]}

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 400
    validator = ResponseValidator(response, logger=logger)
    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)


def test_login_with_missing_username():
    payload = {"password": test_user_password}
    expected_fields = {"username": list}
    expected_values = {"username": ["This field is required."]}

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 400
    validator = ResponseValidator(response, logger=logger)
    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)


def test_login_with_empty_password():
    payload = {"username": test_user_username, "password": ""}
    expected_fields = {"password": list}
    expected_values = {
        "password": ["This field may not be blank."]
        }

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 400
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_time()
    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)


def test_login_with_missing_password():
    payload = {"username": test_user_username}
    expected_fields = {"password": list}
    expected_values = {"password": ["This field is required."]}

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 400
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_time()
    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)


def test_login_with_new_created_user(create_user):
    payload = {
        "username": create_user["email"],
        "password": create_user["password"],
    }
    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 200

    expected_fields = {
        "refresh": str,
        "access": str,
        "id": int,
        "_id": int,
        "username": str,
        "email": str,
        "name": str,
        "isAdmin": bool,
        "token": str,
    }
    expected_values = {
        "id": create_user["id"],
        "_id": create_user["id"],
        "username": create_user["email"],
        "email": create_user["email"],
        "name": create_user["name"],
        "isAdmin": create_user.get("isAdmin", False),
    }
    validator = ResponseValidator(response, logger=logger)
    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)

    delete_user_by_id(create_user["id"])


def test_login_with_deleted_user(create_user):
    user_id = create_user["id"]
    payload = {
        "username": create_user["email"],
        "password": create_user["password"],
    }
    expected_error = {"detail": "No active account found with the given credentials"}

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 200
    delete_user_by_id(user_id)

    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 401
    validator = ResponseValidator(response, logger=logger)
    validator.validate_field_value(expected_error)


def test_login_with_sql_injection():
    payload = {
        "username": "' OR 1=1; --",
        "password": generate_random_password(),
    }
    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 401
    validator = ResponseValidator(response, logger=logger)
    validator.validate_field_value({"detail": "No active account found with the given credentials"})


def test_login_rate_limiting():
    payload = {
        "username": test_user_username, 
        "password": "wrong_password"
        }
    response = None
    for _ in range(10):
        response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
        
    assert response.status_code in [429, 401]
    validator = ResponseValidator(response, logger=logger)
    if response.status_code == 429:
        validator.validate_field_value({"detail": "Request was throttled. Expected available in 60 seconds."})
    else:
        validator.validate_field_value({"detail": "No active account found with the given credentials"})
        
def test_login_with_invalid_json_format():
    payload = "{username: 'invalid_json', password: 'invalid_json'}"
    response = send_request("POST", login_endpoint, payload=payload, headers=headers, logger=logger)
    assert response.status_code == 400
    data = response.json()
    assert "non_field_errors" in data
    assert data["non_field_errors"] == ["Invalid data. Expected a dictionary, but got str."]
