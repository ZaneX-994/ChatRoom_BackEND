from ast import In
from asyncio import run_coroutine_threadsafe
from importlib_metadata import email
import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, auth_register
from src.user import user_profile
@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def user0():
    return auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

@pytest.fixture
def user1():
    return auth_register("a" + VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

# test reset email with duplicate email
def test_duplicated_email(reset, user0, user1):
    reset_result = requests.put(f"{url}user/profile/setemail/v1", json={
        'token': user0['token'],
        'email': "a" + VALID_EMAIL,
    })

    assert reset_result.status_code == InputError.code

# test reset email with Invalid email pattern
def test_invalid_email(reset, user0):
    reset_result = requests.put(f"{url}user/profile/setemail/v1", json={
        'token': user0['token'],
        'email': 'email',
    })

    assert reset_result.status_code == InputError.code

# test reset email with invalid token
def test_with_invalid_token(reset, user0):
    reset_result = requests.put(f"{url}user/profile/setemail/v1", json={
        'token': f"{user0['token']}abc",
        'email': 'abc@example.com',
    })

    assert reset_result.status_code == AccessError.code

# test reset email successfully
def test_reset_successfully(reset, user0):

    reset_result = requests.put(f"{url}user/profile/setemail/v1", json={
        'token': user0['token'],
        'email': 'abc@example.com',
    })

    deets = requests.get(f"{url}user/profile/v1", params={
        'token': user0['token'],
        'u_id': user0['auth_user_id'],
    }).json()['user']

    assert deets['email'] == 'abc@example.com'
    assert reset_result.status_code == 200