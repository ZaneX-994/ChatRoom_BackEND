import pytest
from src.config import url
import requests
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from tests.dm_create_test import user0, user1, user2

SAMPLE_MESSAGE = 'hi'
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


# the request is not from authorised user
def test_message_send_invalid_user(clear, user0, user1, channel_id):
    channel_join(user1, channel_id)
    message_id = send_message(user0, channel_id)
    response = requests.put(f"{url}message/edit/v1", json={
        'token': user1['token'],
        'message_id': message_id,
        'message': 'hi'
    })
    assert response.status_code == 403

# creator edit the message which is user send
def test_message_send_valid_user_creator(clear, user0, user1, channel_id):
    channel_join(user1, channel_id)
    message_id = send_message(user1, channel_id)
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': 'wow'
    })
    message = check_message(user0, channel_id)
    assert len(message) == 1
    assert message[0]['message'] == 'wow'

def test_message_send_invalid_length(clear, user0, channel_id):
    message_id = send_message(user0, channel_id)
    response = requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': 'hi' * 1000
    })
    assert response.status_code == 400

# user is not channel member
def test_invalid_uid_channel(clear, user0, user1, channel_id):
    message_id = send_message(user0, channel_id)
    response = requests.put(f"{url}message/edit/v1", json={
        'token': user1['token'],
        'message_id': message_id,
        'message': 'hello' 
    })
    assert response.status_code == 400

# user is not dm member
def test_invalid_uid_dm(clear, user0, user1, dm_id):
    message_id = send_sample_message(dm_id, user0)
    response = requests.put(f"{url}message/edit/v1", json={
        'token': user1['token'],
        'message_id': message_id,
        'message': 'hello' 
    })
    assert response.status_code == 400

# edit the same message_id
def test_invalid_dm_messaged(clear, user0, dm_id):
    message_id = send_sample_message(dm_id, user0)
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': ''
    })
    response = requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': ''
    })
    assert response.status_code == 400

def test_invalid_channel_messaged(clear, user0, channel_id):
    message_id = send_message(user0, channel_id)
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': ''
    })
    response = requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': ''
    })
    assert response.status_code == 400

def test_invalid_user_not_creator_dm(clear, user0, user2, dm_id):
    message_id = send_sample_message(dm_id, user0)
    response = requests.put(f"{url}message/edit/v1", json={
        'token': user2['token'],
        'message_id': message_id,
        'message': 'hello' 
    })
    assert response.status_code == 403

def test_remove_channel_message(clear, user0, channel_id):
    message_id = send_message(user0, channel_id)
    requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'wow'
    })
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': ''
    })
    message = check_message(user0, channel_id)
    assert len(message) == 1
    assert message[0]['message'] == 'wow'

# creator edit the message which is sent by user2
def test_valid_user_is_creator_edit_dm(clear, user0, user2, dm_id):
    message_id = send_sample_message(dm_id, user2)
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': 'hello' 
    })
    message = check_message_dm(user0, dm_id)
    assert len(message) == 1
    assert message[0]['message'] == 'hello'

# global user edit the message
def test_global_user_edit_channel(clear,user0, user1):
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
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': 'lol'
    })
    message = check_message(user0, channel_id1)
    assert message[0]['message'] == 'lol'

def test_valid_user_creator_remove_dm(clear, user0, user2, dm_id):
    message_id = send_sample_message(dm_id, user2)
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': '' 
    })
    message = check_message_dm(user0, dm_id)
    assert len(message) == 0
    
def test_edit_channel_message(clear, user0, user1, channel_id):
    # Join channel for other user.
    requests.post(f"{url}channel/join/v2", json={
        'token': user1['token'],
        'channel_id': channel_id,
    })
    send_message(user1, channel_id)

    message_id = send_message(user0, channel_id)
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': 'hello'
    })
    message = check_message(user0, channel_id)
    assert message[0]['message'] == 'hello'

def test_edit_dm_message(clear, user0, user2, dm_id):
    send_sample_message(dm_id, user2)
    message_id = send_sample_message(dm_id, user0)

    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': 'hello'
    })
    message = check_message_dm(user0, dm_id)
    assert message[0]['message'] == 'hello'

def test_remove_dm_message(clear, user0, dm_id):
    message_id = send_sample_message(dm_id, user0)
    requests.post(f"{url}message/senddm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': 'wow'
    })
    requests.put(f"{url}message/edit/v1", json={
        'token': user0['token'],
        'message_id': message_id,
        'message': ''
    })
    message = check_message_dm(user0, dm_id)
    assert len(message) == 1
    assert message[0]['message'] == 'wow'

def check_message(user, channel_id):
    """
    Check messages in the channel and return the messages
    """
    response = requests.get(f"{url}channel/messages/v2", params={
        'token': user['token'],
        'channel_id': channel_id,
        'start': 0,
    }).json()
    return response['messages']

def check_message_dm(user, dm_id):
    """
    Check messages in the dm and return the messages
    """
    response = requests.get(f"{url}dm/messages/v1", params={
        'token': user['token'],
        'dm_id': dm_id,
        'start': 0,
    }).json()
    return response['messages']

def send_message(user, channel_id):
    """
    Send the message and return message_id
    """
    response = requests.post(f"{url}message/send/v1", json={
        'token': user['token'],
        'channel_id': channel_id,
        'message': SAMPLE_MESSAGE
    }).json()
    return response['message_id']

def channel_join(user,channel_id):
    """
    User join the channel with channel_id
    """
    requests.post(f"{url}channel/join/v2", json={
        'token': user['token'], 
        'channel_id': channel_id,
    }).json()
    

def send_sample_message(dm_id, user):
    """
    Sends a sample message and returns its id.
    """
    response = requests.post(f"{url}message/senddm/v1", json={
        'token': user['token'],
        'dm_id': dm_id,
        'message': SAMPLE_MESSAGE,
    }).json()
    return response['message_id']
