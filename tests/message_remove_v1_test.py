import pytest
from src.config import url
import requests
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from tests.dm_create_test import user0, user1, user2
from tests.dm_messages_test import send_sample_message
from tests.message_edit_v1_test import send_message, send_sample_message, check_message, check_message_dm, channel_join

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

@pytest.fixture
def dm_id(user0, user2):
    """
    Constructs a DM and returns its dm_id with user0.
    """
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user2['auth_user_id']],
    }).json()
    return result['dm_id']

def test_remove_message_channel(clear, user0, channel_id):
    message_id = send_message(user0, channel_id)
    requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'wow'
    })
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    message = check_message(user0, channel_id)
    assert len(message) == 1
    assert message[0]['message'] == 'wow'  

# Channel creator remove the user message
def test_message_send_valid_user_creator(clear, user0, user1, channel_id):
    channel_join(user1, channel_id)
    message_id = send_message(user1, channel_id)
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    message = check_message(user0, channel_id)
    assert len(message) == 0

def test_remove_message_dm(clear, user0, dm_id):
    message_id = send_sample_message(dm_id, user0)
    requests.post(f"{url}message/senddm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': 'wow'
    })
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    message = check_message_dm(user0, dm_id)
    assert len(message) == 1
    assert message[0]['message'] == 'wow'

# Dm creator remove the user message
def test_valid_user_is_creator_remove_dm(clear, user0, user2, dm_id):
    message_id = send_sample_message(dm_id, user2)
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    message = check_message_dm(user0, dm_id)
    assert len(message) == 0

# Global user remove the message
def test_global_user_remove_channel(clear,user0, user1):
    response = requests.post(f"{url}channels/create/v2", json={
        'token': user1['token'],
        'name': 'channelone',
        'is_public': True,
    }).json()
    channel_id1 = response['channel_id']
    message_id = send_message(user1, channel_id1)
    requests.post(f"{url}channel/join/v2", json={
        'token': user0['token'],
        'channel_id': channel_id1,
    })
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    message = check_message(user0, channel_id1)
    assert len(message) == 0

# User is not creator or authorised user
def test_message_remove_invlid_user(clear, user0, user1, channel_id):
    message_id = send_message(user0, channel_id)
    response = requests.delete(f"{url}message/remove/v1", json={
        'token': user1['token'],
        'message_id': message_id,
    })
    assert response.status_code == 400

def test_message_remove_invlid_token(clear, user0, channel_id):
    message_id = send_message(user0, channel_id)
    response = requests.delete(f"{url}message/remove/v1", json={
        'token': 'x',
        'message_id': message_id,
    })
    assert response.status_code == 403

def test_message_send_user_not_creator(clear, user0, user1, channel_id):
    channel_join(user1, channel_id)
    message_id = send_message(user0, channel_id)
    response = requests.delete(f"{url}message/remove/v1", json={
        'token': user1['token'],
        'message_id': message_id,
    })
    assert response.status_code == 403

def test_invalid_user_not_creator_remove_dm(clear, user0, user2, dm_id):
    message_id = send_sample_message(dm_id, user0)
    response = requests.delete(f"{url}message/remove/v1", json={
        'token': user2['token'],
        'message_id': message_id,
    })
    assert response.status_code == 403

def test_message_dm_remove_invlid_user(clear, user0, user1, dm_id):
    message_id = send_sample_message(dm_id, user0)
    response = requests.delete(f"{url}message/remove/v1", json={
        'token': user1['token'],
        'message_id': message_id,
    })
    assert response.status_code == 400

# remove the same message_id
def test_invalid_dm_messaged(clear, user0, dm_id):
    message_id = send_sample_message(dm_id, user0)
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    response = requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    assert response.status_code == 400

def test_invalid_channel_messaged(clear, user0, channel_id):
    message_id = send_message(user0, channel_id)
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    response = requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })
    assert response.status_code == 400
