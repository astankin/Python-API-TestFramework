# 🧪 Python API Test Framework

A robust, scalable, and easy-to-extend API testing framework built with **Python**, **Pytest**, and modular utilities for request handling, config management, schema validation, and logging.

---

## 📦 Features

- 🔹 Organized test structure with support for **Pytest markers**
- 🔹 Configurable environments using `config.ini`
- 🔹 Custom JSON schema validation
- 🔹 Centralized logging for easy debugging
- 🔹 Support for fixtures (user creation, auth, etc.)
- 🔹 Easily extensible for multiple projects and APIs

---

## 🧰 Tech Stack

- Python 3.8+
- [Pytest](https://docs.pytest.org/)
- `requests` – for HTTP calls
- `jsonschema` – for schema validation
- `loguru` – for structured logging
- `configparser` – to manage environment settings

---

## 📁 Project Structure

```bash
api-test-framework/
│
├── tests/                      # API test cases
│   ├── test_authentication.py
│   └── test_user_management.py
│
├── utilities/                  # Reusable helper modules
│   ├── request_handler.py
│   ├── json_validator.py
│   ├── logger.py
│   ├── read_config.py
│   └── fixtures.py
│
├── schemas/                    # JSON schemas for validation
│   └── user_response_schema.json
│
├── config/
│   └── config.ini              # Environment-specific settings
│
├── requirements.txt
├── pytest.ini
└── README.md
