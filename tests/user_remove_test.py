import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
from tests.dm_messages_test import send_sample_message
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, auth_register


@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")


@pytest.fixture
def user0():
    return auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)


# Not a fixture as we need to be able to invoke it directly.
def target_user():
    return auth_register("a" + VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)


def test_user_remove_successful(reset, user0):
    # Create target user.
    user1 = target_user()

    # Create channel with target user.
    requests.post(f"{url}channels/create/v2", json={
        'token': user1['token'],
        'name': 'General',
        'is_public': True,
    }).json()

    # Create DM.
    dm_id = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()['dm_id']

    # Send messages.
    send_sample_message(dm_id, user1)

    # Remove user.
    result = requests.delete(f"{url}admin/user/remove/v1", json={
        'token': user0['token'], 
        'u_id': user1['auth_user_id'],
    }).json()
    assert result == {}
    
    # Check message contents are replaced.
    messages = requests.get(f"{url}dm/messages/v1", params={
        r'token': user0['token'],
        'dm_id': dm_id,
        'start': 0,
    }).json()['messages']
    for message in messages:
        assert message['message'] == "Removed user"

    # Check profile retrievable.
    profile = requests.get(f"{url}user/profile/v1", params={
        'token': user0['token'],
        'u_id': user1['auth_user_id'],
    }).json()['user']

    # Check retrieved name.
    assert profile['name_first'] == "Removed"
    assert profile['name_last'] == "user"

    # Check reuse of email and handle.
    assert 'auth_user_id' in target_user()

    # Check deleted user cannot access endpoints.
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user1['token'],
        'u_ids': [],
    })
    assert result.status_code == AccessError.code


def test_remove_user_twice(reset, user0):
    # Create target user.
    user1 = target_user()

    # Delete user once.
    result = requests.delete(f"{url}admin/user/remove/v1", json={
        'token': user0['token'], 
        'u_id': user1['auth_user_id'],
    }).json()
    assert result == {}

    # Delete user again.
    result = requests.delete(f"{url}admin/user/remove/v1", json={
        'token': user0['token'], 
        'u_id': user1['auth_user_id'],
    })
    assert result.status_code == InputError.code


# Check invalid target user.
def test_user_remove_invalid_user(reset, user0):
    result = requests.delete(f"{url}admin/user/remove/v1", json={
        'token': user0['token'], 
        'u_id': user0['auth_user_id'] + 1,
    })
    assert result.status_code == InputError.code


# Check removing only owner (itself).
def test_user_remove_only_owner(reset, user0):
    result = requests.delete(f"{url}admin/user/remove/v1", json={
        'token': user0['token'], 
        'u_id': user0['auth_user_id'],
    })
    assert result.status_code == InputError.code


# Check unauthorized.
def test_user_remove_unauthorized(reset, user0):
    user1 = target_user()
    result = requests.delete(f"{url}admin/user/remove/v1", json={
        'token': user1['token'], 
        'u_id': user1['auth_user_id'],
    })
    assert result.status_code == AccessError.code

