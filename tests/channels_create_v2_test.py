from unittest import result
from urllib import response
from flask import config
import requests
from src.config import url
import pytest
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME
from src.error import AccessError, InputError
VALID_NAME = 'channelOne'
IS_PUBLIC = True
INVALID_NAME = 'n' * 21

@pytest.fixture
def reset():
    requests.delete(f'{url}clear/v1')

@pytest.fixture
def details():
    return {
        "email": VALID_EMAIL,
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }

# test if one channel is created successfully
def test_channel_created_successfully(reset, details):
    register_result = requests.post(f"{url}auth/register/v2", json=details)
    result = register_result.json()

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': result['token'],
        'name': VALID_NAME,
        'is_public': IS_PUBLIC,
    })

    assert register_result.status_code == 200
    assert newChannel.status_code == 200

# test create channel with invalid name
def test_channel_create_with_empty_name(reset, details):
    register_result = requests.post(f"{url}auth/register/v2", json=details)
    result = register_result.json()

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': result['token'],
        'name': '',
        'is_public': IS_PUBLIC,
    })
    assert newChannel.status_code == InputError.code

# test create channel with overlong name
def test_channel_create_with_long_name(reset, details):
    register_result = requests.post(f"{url}auth/register/v2", json=details)
    result = register_result.json()
    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': result['token'],
        'name': INVALID_NAME,
        'is_public': IS_PUBLIC,
    })
    assert newChannel.status_code == InputError.code

#test create channel wih invalid token
def test_channel_create_with_wrong_token(reset, details):
    register_result = requests.post(f"{url}auth/register/v2", json=details)
    result = register_result.json()
    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': f"{result['token']}123",
        'name': VALID_NAME,
        'is_public': IS_PUBLIC,
    })
    assert newChannel.status_code == AccessError.code