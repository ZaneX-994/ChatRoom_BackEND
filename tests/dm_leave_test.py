import pytest
import requests
from src.config import url
from src.error import InputError, AccessError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, auth_register
from tests.dm_create_test import user0, user1

@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")

# test dm_leave with invalid dm_id
def test_with_invalid_dm_id(reset, user0, user1):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()

    leave_result = requests.post(f"{url}dm/leave/v1", json={
        'token': user1['token'],
        'dm_id': result['dm_id'] + 1,
    })

    assert leave_result.status_code == InputError.code

# test dm_leave with invalidate token
def test_with_invalidate_token(reset, user0, user1):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()

    leave_result = requests.post(f"{url}dm/leave/v1", json={
        'token': f"{user1['token']}123",
        'dm_id': result['dm_id'],
    })

    assert leave_result.status_code == AccessError.code

# test if user not a member of DM
def test_user_not_a_memebr(reset, user0, user1):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [],
    }).json()

    leave_result = requests.post(f"{url}dm/leave/v1", json={
        'token': user1['token'],
        'dm_id': result['dm_id'],
    })

    assert leave_result.status_code == AccessError.code

# test leave successfully
def test_dm_leave_with_success(reset, user0, user1):
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()

    leave_result = requests.post(f"{url}dm/leave/v1", json={
        'token': user1['token'],
        'dm_id': result['dm_id'],
    })

    assert leave_result.status_code == 200