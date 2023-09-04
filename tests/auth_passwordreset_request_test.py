import pytest
import requests

from src.config import url
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME
from src.error import AccessError

@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def userOne():
    return {
        "email": VALID_EMAIL,
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }

# test return type of auth/passwordreset/request/v1 
def test_return(reset, userOne):
    requests.post(f"{url}auth/register/v2", json=userOne)

    reset_result = requests.post(f"{url}auth/passwordreset/request/v1", json={
        'email': userOne['email'],
    }).json()

    assert reset_result == {}

# test user is logged out after sending request
def test_if_logged_out(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()

    requests.post(f"{url}auth/passwordreset/request/v1", json={
        'email': userOne['email'],
    })

    log_out_result = requests.post(f"{url}auth/logout/v1", json={
        'token': register_result['token'],
    })

    assert log_out_result.status_code == AccessError.code

# test user not registered
def test_user_not_exist(reset):
    
    reset_result = requests.post(f"{url}auth/passwordreset/request/v1", json={
        'email': VALID_EMAIL,
    })

    assert reset_result.status_code == 200
    assert reset_result.json() == {}
