import requests
import pytest
from jsonschema import validate, ValidationError

# class ResponseValidator:

#     @staticmethod
#     def validate_response_headers(response, expected_content_type="application/json; charset=utf-8"):
#         """
#         Validates the Content-Type header in the response.

#         :param response: The response object from the API request.
#         :param expected_content_type: The expected Content-Type header value, including charset.
#         """
#         try:
#             actual_content_type = response.headers.get("Content-Type")
#             assert actual_content_type is not None, "Content-Type header is missing in the response"
#             assert expected_content_type in actual_content_type, (
#                 f"Expected Content-Type: {expected_content_type}, but got: {actual_content_type}"
#             )
#         except AssertionError as e:
#             raise AssertionError(f"Header validation failed: {e}")

#     @staticmethod
#     def validate_response_time(response, max_response_time_ms=200):
#         """
#         Validates the response time of an API request in milliseconds.

#         :param response: The response object from the API request.
#         :param max_response_time_ms: The maximum allowable response time in milliseconds.
#         """
#         response_time_ms = response.elapsed.total_seconds() * 1000
#         assert response_time_ms <= max_response_time_ms, (
#             f"Response time exceeded the limit! "
#             f"Expected <= {max_response_time_ms} ms, but got {response_time_ms:.2f} ms."
#         )

#     @staticmethod
#     def validate_data_type(response, field_validations=None):
#         data = response.json()
#         assert isinstance(data, dict), (
#             f"Expected data to be of type dict, but got {type(data).__name__}"
#         )

#         if field_validations:
#             for field, field_type in field_validations.items():
#                 assert field in data, f"Field '{field}' is missing in the data."
#                 assert isinstance(data[field], field_type), (
#                     f"Field '{field}' expected to be of type {field_type.__name__}, but got {type(data[field]).__name__}"
#                 )

#     @staticmethod
#     def validate_field_value(response, field_validations=None):
#         data = response.json()
#         if field_validations:
#             for field, value in field_validations.items():
#                 assert data[field] == value, f"Value of '{field}' expected to be of type {value}, but got {data[field]}"

#     @staticmethod
#     def validate_json_schema(response, schema):
#         data = response.json()
#         try:
#             validate(instance=data, schema=schema)
#         except ValidationError as e:
#             print(f"JSON validation error: {e.message}")
#             assert False


class ResponseValidator:
    def __init__(self, response, logger=None):
        self.response = response
        self.data = response.json()
        self.logger = logger

    def validate_response_headers(self, expected_content_type="application/json"):
        actual_content_type = self.response.headers.get("Content-Type")
        assert actual_content_type and expected_content_type in actual_content_type, (
            f"Expected Content-Type: {expected_content_type}, but got: {actual_content_type}"
        )

    def validate_response_time(self, max_response_time_ms=200):
        response_time_ms = self.response.elapsed.total_seconds() * 1000
        assert response_time_ms <= max_response_time_ms, (
            f"Expected <= {max_response_time_ms} ms, but got {response_time_ms:.2f} ms."
        )

    def validate_data_type(self, field_validations):
        for field, field_type in field_validations.items():
            assert field in self.data, f"Missing field: {field}"
            assert isinstance(self.data[field], field_type), (
                f"Expected '{field}' to be type {field_type.__name__}, got {type(self.data[field]).__name__}"
            )

    def validate_field_value(self, field_validations):
        for field, expected_value in field_validations.items():
            assert self.data[field] == expected_value, (
                f"Expected '{field}' = {expected_value}, got {self.data[field]}"
            )

    def validate_json_schema(self, schema):
        try:
            validate(instance=self.data, schema=schema)
        except ValidationError as e:
            raise AssertionError(f"JSON Schema validation error: {e.message}")

