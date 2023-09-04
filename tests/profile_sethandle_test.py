import pytest
import requests

from src.config import url
from src.error import InputError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, auth_register


@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")


@pytest.fixture
def john_doe():
    return auth_register(VALID_EMAIL, VALID_PASSWORD, "John", "Doe")


def test_profile_sethandle_successful(reset, john_doe):
    result = requests.put(f"{url}user/profile/sethandle/v1", json={
        'token': john_doe['token'],
        'handle_str': "johnny727",
    }).json()
    assert result == {}


def test_profile_sethandle_length(reset, john_doe):
    # Too short.
    result = requests.put(f"{url}user/profile/sethandle/v1", json={
        'token': john_doe['token'],
        'handle_str': "12",
    })
    assert result.status_code == InputError.code

    # Too long.
    result = requests.put(f"{url}user/profile/sethandle/v1", json={
        'token': john_doe['token'],
        'handle_str': "a" * 21,
    })
    assert result.status_code == InputError.code


def test_profile_sethandle_non_alphanumeric(reset, john_doe):
    result = requests.put(f"{url}user/profile/sethandle/v1", json={
        'token': john_doe['token'],
        'handle_str': "ab😊",
    })
    assert result.status_code == InputError.code


def test_profile_sethandle_conflict(reset, john_doe):
    # Try to set user1's handle to john's.
    user1 = auth_register("a" + VALID_EMAIL, VALID_PASSWORD, "Joe", "Mama")
    result = requests.put(f"{url}user/profile/sethandle/v1", json={
        'token': user1['token'],
        'handle_str': "johndoe",
    })
    assert result.status_code == InputError.code

