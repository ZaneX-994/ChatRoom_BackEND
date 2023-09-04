import pytest
import requests

from src.config import url
from src.error import InputError
from src.dm import construct_dm_name
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, auth_register


@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")


@pytest.fixture
def user0():
    return auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

@pytest.fixture
def user1():
    return auth_register("a" + VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

@pytest.fixture
def user2():
    return auth_register("b" + VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)


def test_dm_create_successful(reset, user0):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [],
    }).json()
    assert 'dm_id' in result


def test_dm_create_successful_two_users(reset, user0, user1):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()
    assert 'dm_id' in result


def test_dm_create_three_users(reset, user0, user1, user2):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id'], user2['auth_user_id']],
    }).json()
    assert 'dm_id' in result


# Ensure errors with duplicate user listed.
def test_dm_create_duplicate_user(reset, user0, user1):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id'], user1['auth_user_id']],
    })
    assert result.status_code == InputError.code


# Ensure errors with invalid user listed.
def test_dm_create_invalid_user(reset, user0):
    invalid_id = user0['auth_user_id'] + 1
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [invalid_id],
    })
    assert result.status_code == InputError.code


# Test construction of the dm name from user handles.
def test_construct_dm_name():
    handles = ['chandle3', 'bhandle2', 'ahandle1']
    assert construct_dm_name(handles) == "ahandle1, bhandle2, chandle3"

