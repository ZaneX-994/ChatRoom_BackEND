import pytest
from src.config import url
import requests
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from tests.dm_create_test import user0, user1

SAMPLE_MESSAGE = "hi"

@pytest.fixture
def clear():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def channel_id(user0):
    response = requests.post(f"{url}channels/create/v2", json={
        'token': user0['token'],
        'name': 'channelone',
        'is_public': True,
    }).json()
    return response['channel_id']
    
def test_bad_parameters(clear, user0, channel_id):
    response = requests.get(f"{url}channel/messages/v2", params={
        'token': 1,
        'channel_id': channel_id,
        'start': 0,
    })
    assert response.status_code == 403

    response = requests.get(f"{url}channel/messages/v2", params={
        'token': user0['token'],
        'channel_id': 4,
        'start': 0,
    })
    assert response.status_code == 400

def test_bad_start(clear, user0, channel_id):
    response = requests.get(f"{url}channel/messages/v2", params={
        'token': user0['token'],
        'channel_id': channel_id,
        'start': 2,
    })
    assert response.status_code == 400

# user is not member of the channel
def test_not_member(clear, user0, user1, channel_id):
    response = requests.get(f"{url}channel/messages/v2", params={
        'token': user1['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert response.status_code == 403

# check one message
def test_message1(clear, user0, channel_id):
    message_id = send_message(user0, channel_id)
    response = requests.get(f"{url}channel/messages/v2", params={
        'token': user0['token'],
        'channel_id': channel_id,
        'start': 0,
    }).json()

    assert len(response['messages']) == 1
    assert response['start'] == 0
    assert response['end'] == -1

    message = response['messages'][0]
    assert message['message_id'] == message_id
    assert message['u_id'] == user0['auth_user_id']
    assert message['message'] == SAMPLE_MESSAGE
    assert 'time_sent' in message

# check 50 message and the last one message is new
def test_message_50(clear, user0, channel_id):
    for _i in range(50):
        send_message(user0, channel_id)
    response = requests.get(f"{url}channel/messages/v2", params={
        'token': user0['token'],
        'channel_id': channel_id,
        'start': 0,
    }).json()
    assert len(response['messages']) == 50
    assert response['start'] == 0
    assert response['end'] == -1

def test_message_100(clear, user0, channel_id):
    for _i in range(100):
        send_message(user0, channel_id)
    response = requests.get(f"{url}channel/messages/v2", params={
        'token': user0['token'],
        'channel_id': channel_id,
        'start': 0,
    }).json()
    assert len(response['messages']) == 50
    assert response['start'] == 0
    assert response['end'] == 50

def send_message(user, channel_id):
    """
    Seed the message in the channel and return the message_id
    """
    response = requests.post(f"{url}message/send/v1", json={
        'token': user['token'],
        'channel_id': channel_id,
        'message': SAMPLE_MESSAGE,
    }).json()
    return response['message_id']
