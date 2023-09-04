import pytest
from src.config import url
import requests
from src.error import InputError, AccessError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, auth_register
import time
valid_message = "A random message"
VALID_NAME = 'channelOne'
invalid_message = "A" * 1001
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
def test_token_invalidate(reset, userOne):

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    standup_send_result = requests.post(f"{url}standup/send/v1", json={
        'token': userOne['token'] + '1',
        'channel_id': newChannel['channel_id'],
        'message': valid_message,
    })

    assert standup_send_result.status_code == AccessError.code

# test when channel_id not refer to a valid channel
def test_invalid_channel_id(reset, userOne):

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    standup_send_result = requests.post(f"{url}standup/send/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'] + 1,
        'message': valid_message,
    })

    assert standup_send_result.status_code == InputError.code

# test overlong message
def test_invalid_message_length(reset, userOne):

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    standup_send_result = requests.post(f"{url}standup/send/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'message': invalid_message,
    })

    assert standup_send_result.status_code == InputError.code

# test when the no active standup is running in the channel
def test_no_standup_is_running(reset, userOne):
    
    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    standup_send_result = requests.post(f"{url}standup/send/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'message': valid_message,
    })

    assert standup_send_result.status_code == InputError.code

# test user not in the channel
def test_not_in_channel(reset, userOne, userTwo):
    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    standup_send_result = requests.post(f"{url}standup/send/v1", json={
        'token': userTwo['token'],
        'channel_id': newChannel['channel_id'],
        'message': valid_message,
    })

    assert standup_send_result.status_code == AccessError.code

# test the return type / success send
def test_return(reset, userOne):

    newChannel = requests.post(f'{url}channels/create/v2', json={
        'token': userOne['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    requests.post(f"{url}standup/start/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'length': CONSTANT_LENGTH,
    })

    standup_send_result = requests.post(f"{url}standup/send/v1", json={
        'token': userOne['token'],
        'channel_id': newChannel['channel_id'],
        'message': valid_message,
    })

    time.sleep(CONSTANT_LENGTH + 1)
    
    assert standup_send_result.status_code == 200
    assert standup_send_result.json() == {}