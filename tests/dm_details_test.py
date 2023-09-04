import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
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
@pytest.fixture
def userTwo():
    return{
        "email": 'b@example.com',
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }
# test invalid token
def test_dm_detail_with_invalid_token(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()
    arguments = {
        'token': register_result['token'],
        'u_ids': [],
    }
    dm_create_result = requests.post(f"{url}dm/create/v1", json=arguments).json()
    dm_detail_result = requests.get(f"{url}dm/details/v1", params={
        'token': f"{register_result['token']}123",
        'dm_id': dm_create_result['dm_id']
    })

    assert dm_detail_result.status_code == AccessError.code

# test invalid dm_id
def test_dm_detail_with_invalid_dm_id(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()

    dm_detail_result = requests.get(f"{url}dm/details/v1", params={
        'token': register_result['token'],
        'dm_id': 100,
    })

    assert dm_detail_result.status_code == InputError.code

# test get dm detail successfully
def test_dm_detail_get_with_success(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()
    arguments = {
        'token': register_result['token'],
        'u_ids': [],
    }
    dm_create_result = requests.post(f"{url}dm/create/v1", json=arguments).json()
    dm_detail_result = requests.get(f"{url}dm/details/v1", params={
        'token': register_result['token'],
        'dm_id': dm_create_result['dm_id']
    })

    assert dm_detail_result.status_code == 200

# test if user is not a member of the dm
def test_dm_detail_with_non_member(reset, userOne, userTwo):
    userOne_registion = requests.post(f"{url}auth/register/v2", json=userOne).json()
    userTwo_registion = requests.post(f"{url}auth/register/v2", json=userTwo).json()
    arguments = {
        'token': userOne_registion['token'],
        'u_ids': [],
    }
    dm_create_result = requests.post(f"{url}dm/create/v1", json=arguments).json()
    dm_detail_result = requests.get(f"{url}dm/details/v1", params={
        'token': userTwo_registion['token'],
        'dm_id': dm_create_result['dm_id']
    })

    assert dm_detail_result.status_code == AccessError.code
