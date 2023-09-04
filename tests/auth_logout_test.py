from re import S
import pytest
import requests

from src.config import url
from src.error import AccessError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME

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

# test logout successfully
def test_successfull_logout(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()
    
    token = register_result['token']
    logout_result = requests.post(f"{url}auth/logout/v1", json={'token': token})
    
    assert logout_result.status_code == 200

# test for already logged out user
def test_logout_with_invalid_token(reset, userOne):
    requests.post(f"{url}auth/register/v2", json=userOne).json()
    login_result = requests.post(f"{url}auth/login/v2", json={
        "email": userOne["email"], 
        "password": userOne["password"]
    }).json()
    token = login_result['token']

    logout_result = requests.post(f"{url}auth/logout/v1", json={'token': token})
    assert logout_result.status_code == 200

    logout_result = requests.post(f"{url}auth/logout/v1", json={'token': token})
    assert logout_result.status_code == AccessError.code
    
# test for invalid token
def test_invalid_token(reset, userOne):
    requests.post(f"{url}auth/register/v2", json=userOne).json()
    login_result = requests.post(f"{url}auth/login/v2", json={
        "email": userOne["email"], 
        "password": userOne["password"]
    }).json()
    token = login_result['token']

    logout_result = requests.post(f"{url}auth/logout/v1", json={'token': f"{token}123"})
    
    assert logout_result.status_code == AccessError.code