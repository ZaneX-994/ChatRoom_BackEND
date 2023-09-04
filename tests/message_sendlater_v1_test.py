import pytest
from src.config import url
import requests
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from tests.dm_create_test import user0, user1
import time
from tests.message_edit_v1_test import check_message
import threading

@pytest.fixture
def clear():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def channel_id(user0):
    """
    Constructs a channel and returns its dm_id with user0.
    """
    response = requests.post(f"{url}channels/create/v2", json={
        'token': user0['token'],
        'name': 'channelone',
        'is_public': True,
    }).json()
    return response['channel_id']

@pytest.fixture
def time_sent(clear):
    """
    Create the time to sendlater
    """
    time_sent = time.time()
    return time_sent + 1

def test_bad_parameters(clear, channel_id, time_sent):
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': 1,
        'channel_id': channel_id,
        'message': '1',
        'time_sent': time_sent,
    })
    assert response.status_code == AccessError.code

def test_invalid_channel_id(clear, user0, time_sent):
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': user0['token'],
        'channel_id': '3',
        'message': '1',
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code

def test_invalid_length_long(clear, user0, channel_id, time_sent):
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'hi' * 1000,
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': '',
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code

def test_invalid_time_send(clear, user0, channel_id):
    time_now = time.time()
    invalid_time = time_now - 1
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'hi',
        'time_sent': invalid_time,
    })
    assert response.status_code == InputError.code

def test_user_not_channel_members(clear, user0, user1, channel_id, time_sent):
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'hi',
        'time_sent': time_sent,
    })
    assert response.status_code == AccessError.code

def test_sendlater_message(clear, user0, channel_id, time_sent):
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'hi',
        'time_sent': time_sent,
    })
    assert response.status_code == 200
    # Wait 1 second for check the messsage after sendlater
    time.sleep(1)
    message = check_message(user0, channel_id)
    assert message[0]['message'] == 'hi'
    
# Check message at unsuitable time
def test_invalid_sendlater_message(clear, user0, channel_id, time_sent):
    response = requests.post(f"{url}message/sendlater/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'hi',
        'time_sent': time_sent,
    })
    assert response.status_code == 200
    message = check_message(user0, channel_id)
    assert len(message) == 0