import pytest
import requests

from src.config import url
from src.error import InputError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME

@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")


@pytest.fixture
def details():
    return {
        "email": VALID_EMAIL,
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }


# Test for valid logins.
def test_auth_login_valid(reset, details):
    register_result = requests.post(f"{url}auth/register/v2", json=details).json()
    login_result = requests.post(f"{url}auth/login/v2", json={
        "email": details["email"], 
        "password": details["password"]
    }).json()

    assert register_result['auth_user_id'] == login_result['auth_user_id']
    assert 'token' in register_result
    assert 'token' in login_result


# Test for invalid password.
def test_auth_login_invalid_password(reset, details):
    requests.post(f"{url}auth/register/v2", json=details).json()
    result = requests.post(f"{url}auth/login/v2", json={
        "email": details["email"], 
        "password": details["password"] + "a"
    })
    assert result.status_code == InputError.code


# Test for bad email.
def test_auth_login_unregistered_email(reset, details):
    result = requests.post(f"{url}auth/login/v2", json={
        "email": details["email"], 
        "password": details["password"] + "a"
    })
    assert result.status_code == InputError.code


