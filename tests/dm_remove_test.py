import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
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

# test remove dm with invalid dm_id
def test_with_invalid_dm_id(reset, user0):
    create_result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [],
    }).json()

    remove_result = requests.delete(f"{url}dm/remove/v1", json={
        'token': user0['token'],
        'dm_id': create_result['dm_id'] + 1,
    })

    assert remove_result.status_code == InputError.code


# test remove dm with invalidate token
def test_with_invalid_token(reset, user0, user1):
    create_result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()

    remove_result = requests.delete(f"{url}dm/remove/v1", json={
        'token': user1['token'],
        'dm_id': create_result['dm_id'],
    })
    
    assert remove_result.status_code == AccessError.code

# test remove dm with user not in dm
def test_not_member_of_dm(reset, user0, user1, user2):
    create_result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id'], user2['auth_user_id']],
    }).json()

    leave_result = requests.post(f"{url}dm/leave/v1", json={
        'token': user0['token'],
        'dm_id': create_result['dm_id'],
    })

    remove_result = requests.delete(f"{url}dm/remove/v1", json={
        'token': user0['token'],
        'dm_id': create_result['dm_id'],
    })

    assert leave_result.status_code == 200
    assert remove_result.status_code == AccessError.code

# test remove with success
def test_remove_successfully(reset, user0, user1, user2):
    create_result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id'], user2['auth_user_id']],
    }).json()

    remove_result = requests.delete(f"{url}dm/remove/v1", json={
        'token': user0['token'],
        'dm_id': create_result['dm_id'],
    })
    
    assert remove_result.status_code == 200

    dm_list = requests.get(f"{url}dm/list/v1",params={
        'token': user0['token'],
    }).json()

    assert dm_list['dms'] == []