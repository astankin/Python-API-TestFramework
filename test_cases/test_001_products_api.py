import pytest
from utilities.get_token import get_auth_token
from utilities.json_validator import ResponseValidator
from utilities.logger import setup_logger
from utilities.read_config import ReadConfig
from utilities.request_handler import send_request
from utilities.schema_loader import load_json_schema

# ----- Global Setup -----
logger = setup_logger(log_file_path=ReadConfig.get_logs_product_path())
endpoint = ReadConfig.get_products_endpoint()
product_id = 1
product_schema = load_json_schema("product_schema.json")
all_product_schema = load_json_schema("all_products_schema.json")
headers = {'Content-Type': 'application/json'}

# ----- Fixture for creating and deleting a product -----
@pytest.fixture
def created_product():
    token = get_auth_token()
    auth_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload = {
        "name": "Fixture Product",
        "image": "/images/test_fixture.jpg",
        "brand": "BrandFixture",
        "category": "CategoryFixture",
        "description": "Created from fixture",
        "price": "99.99",
        "countInStock": 5
    }

    response = send_request(
        method="POST",
        endpoint=f"{endpoint}/create/",
        headers=auth_headers,
        payload=payload,
        logger=logger
    )
    assert response.status_code == 200, f"Setup failed with status: {response.status_code}"

    product_id = response.json().get("_id")
    yield {
        "id": product_id,
        "response": response,
        "headers": auth_headers,
        "payload": payload
    }

    send_request(
        method="DELETE",
        endpoint=f"{endpoint}/delete/{product_id}/",
        headers=auth_headers,
        logger=logger
    )
    logger.info(f"Deleted test product with ID {product_id}")

def cleanup(product_id, auth_headers):
    if product_id:
        send_request(
            method="DELETE",
            endpoint=f"{endpoint}/delete/{product_id}/",
            headers=auth_headers,
            logger=logger
        )
        logger.info(f"Deleted test product with ID {product_id}")


# ----- Tests -----

def test_get_products_list():
    logger.info("*** Starting test: test_get_products_list ***")
    response = send_request(
        method="GET",
        endpoint=endpoint,
        headers=headers,
        logger=logger
    )

    assert response.status_code == 200
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()
    validator.validate_json_schema(schema=all_product_schema)


def test_get_product_by_id():
    logger.info("*** Starting test: test_get_product_by_id ***")
    response = send_request(
        method="GET",
        endpoint=f"{endpoint}/{product_id}",
        headers=headers,
        logger=logger
    )

    assert response.status_code == 200
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()
    validator.validate_json_schema(schema=product_schema)

    expected_fields = {
        "_id": int,
        "reviews": list,
        "name": str,
        "image": str,
        "brand": str,
        "category": str,
        "description": str,
        "rating": str,
        "numReviews": int,
        "price": str,
        "countInStock": int,
        "createdAt": str,
        "user": int
    }

    expected_values = {
        "_id": 1,
        "name": "Airpods Wireless Bluetooth Headphones",
        "image": "/images/airpods_rueLkRx.jpg",
        "brand": "Apple",
        "category": "Electronics",
        "description": "Bluetooth technology lets you connect it with compatible devices wirelessly High-quality AAC audio offers immersive listening experience Built-in microphone allows you to take calls while working",
        "rating": "3.00",
        "numReviews": 2,
        "price": "1998.99",
        "countInStock": 18,
        "createdAt": "2024-08-13T19:30:16.537131Z",
        "user": 1
    }

    validator.validate_data_type(expected_fields)
    validator.validate_field_value(expected_values)


def test_create_product(created_product):
    data = created_product
    response = data["response"]
    payload = data["payload"]

    assert response.status_code == 200
    json_data = response.json()
    
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()


    assert json_data["name"] == payload["name"]
    assert json_data["brand"] == payload["brand"]
    assert json_data["category"] == payload["category"]
    assert json_data["description"] == payload["description"]
    assert json_data["price"] == payload["price"]
    assert json_data["countInStock"] == payload["countInStock"]
    assert isinstance(json_data.get("_id"), int)
    assert "createdAt" in json_data
    assert json_data["rating"] == None
    assert json_data["numReviews"] == 0


def test_create_product_unauthorized():
    payload = {
        "name": "Unauthorized Product",
        "image": "/images/unauth.jpg",
        "brand": "NoAuth",
        "category": "Invalid",
        "description": "No token provided.",
        "price": "0.00",
        "countInStock": 0
    }
    
    error_schema = {
        "type": "object",
        "properties": {
            "detail": {"type": "string"}
        },
        "required": ["detail"],
        "additionalProperties": False
    }

    response = send_request(
        method="POST",
        endpoint=f"{endpoint}/create/",
        headers={'Content-Type': 'application/json'},  # No auth
        payload=payload,
        logger=logger
    )
    json_data = response.json()
    
    validator = ResponseValidator(response, logger=logger)
    validator.validate_response_headers()
    validator.validate_response_time()
    validator.validate_json_schema(schema=error_schema)
    
    assert json_data.get("detail") == "Authentication credentials were not provided.", "Unexpected error message"
    assert "name" not in json_data, "Name should not be present in unauthorized response"
    assert response.status_code in [401, 403], f"Expected 401/403 Unauthorized, got {response.status_code}"
    

def test_create_product_missing_name():
    token = get_auth_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload = {
        # "name" is intentionally missing
        "image": "/images/test.jpg",
        "brand": "Test",
        "category": "TestCat",
        "description": "Missing name field",
        "price": "10.00",
        "countInStock": 5
    }

    response = send_request(
        method="POST",
        endpoint=f"{endpoint}/create/",
        headers=headers,
        payload=payload,
        logger=logger
    )

    assert response.status_code == 200, f"Expected 200 for missing name, got {response.status_code}"
    product_id = response.json().get("_id")
    cleanup(product_id, headers)


def test_create_product_invalid_price_format():
    token = get_auth_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload = {
        "name": "Bad Price Product",
        "image": "/images/test.jpg",
        "brand": "BrandX",
        "category": "CatX",
        "description": "Invalid price format",
        "price": "abc",  # Invalid
        "countInStock": 5
    }

    response = send_request(
        method="POST",
        endpoint=f"{endpoint}/create/",
        headers=headers,
        payload=payload,
        logger=logger
    )

    assert response.status_code in [400, 500], f"Expected 400/500 for invalid price, got {response.status_code}"
    
def test_create_product_invalid_count_in_stock():
    token = get_auth_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }           
    
    payload = {
        "name": "Invalid Stock Product",    
        "image": "/images/test.jpg",
        "brand": "BrandY",
        "category": "CatY",
        "description": "Invalid countInStock format",
        "price": "10.00",
        "countInStock": "five"  # Invalid
    }   
    
    response = send_request(
        method="POST",
        endpoint=f"{endpoint}/create/",
        headers=headers,            
        payload=payload,
        logger=logger
    )
    assert response.status_code in [400, 500], f"Expected 400/500 for invalid countInStock, got {response.status_code}"
    
