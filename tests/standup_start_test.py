import pytest
from src.config import url
import requests
from src.error import InputError, AccessError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, auth_register
import time

VALID_NAME = 'channelOne'
valid_message = "A random message"
CONSTANT_LENGTH = 2

@pytest.fixture
def reset():
    requests.delete(f"{url}/clear/v1")

@pytest.fixture
def userOne():
    return auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)
    

@pytest.fixture
def userTwo():
    return auth_register("a" + VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)


# test invalid token
def test_invalid_token(reset, userOne):

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': 'VALID_NAME',
        'is_public': True,
    }).json()

    standup_start_result = requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'] + '1',
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    assert standup_start_result.status_code == AccessError.code

# test when user is not in the channel
def test_user_not_in_channel(reset, userOne, userTwo):

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': 'VALID_NAME',
        'is_public': True,
    }).json()

    standup_start_result = requests.post(f"{url}standup/start/v1", json={
        'token': userTwo['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    assert standup_start_result.status_code == AccessError.code

# test channel_id doesn't refer to a valid channel
def test_channel_id_not_valid(reset, userOne):

    standup_start_result = requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': 123,
        'length': CONSTANT_LENGTH,
    })

    assert standup_start_result.status_code == InputError.code

# test when length is negative
def test_negative_length(reset, userOne):

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    standup_start_result = requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': -CONSTANT_LENGTH,
    })

    assert standup_start_result.status_code == InputError.code

# test an active standup is currenctly running in the channel
def test_an_active_standup_is_running(reset, userOne, userTwo):
    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    requests.post(f"{url}channel/invite/v2", json = {
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'u_id': userTwo['auth_user_id'],
    })

    requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    standup_start_result = requests.post(f"{url}standup/start/v1", json={
        'token': userTwo['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    assert standup_start_result.status_code == InputError.code

# test standup_start successfully
def test_success(reset, userOne):
    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    standup_start_result = requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    }).json()

    time.sleep(CONSTANT_LENGTH + 1)

    assert 'time_finish' in standup_start_result

