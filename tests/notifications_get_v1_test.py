from contextlib import AsyncExitStack
import pytest
from src.config import url
import requests
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from tests.dm_create_test import user0, user1, user2

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
def dm_id(user0, user1):
    """
    Constructs a DM and returns its dm_id with user0.
    """
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()
    return result['dm_id']

def test_invalid_token(clear, user0):
    response = requests.get(f"{url}notifications/get/v1", params={
        'token': 1
    })
    assert response.status_code == AccessError.code

def test_channel_invite(clear, user0, user1, user2, channel_id):
    requests.post(f"{url}channel/invite/v2", json={
        'token': user0['token'], 
        'channel_id': channel_id,
        'u_id': user1['auth_user_id']
    })
    requests.post(f"{url}channel/invite/v2", json={
        'token': user0['token'], 
        'channel_id': channel_id,
        'u_id': user2['auth_user_id']
    })
    response = requests.get(f"{url}notifications/get/v1", params={
        'token': user1['token']
    })
    assert response.status_code == 200
    response = response.json()
    assert len(response['notifications']) == 1

def test_dm_invite(clear, user0, user1, user2, dm_id):
    requests.post(f"{url}dm/create/v1", json={
        'token': user2['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()
    requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user2['auth_user_id']],
    }).json()
    response = requests.get(f"{url}notifications/get/v1", params={
        'token': user1['token']
    })
    assert response.status_code == 200
    response = response.json()
    assert len(response['notifications']) == 2

def test_tagged_message(clear,user0, channel_id):
    user1_info = {
        'email': "Ethans@protonmail.com",
        'password': "aD1#bl",
        'name_first': "Ethan",
        'name_last': "s",
    }
    user2_info = {
        'email': "Ethanh@protonmail.com",
        'password': "aD1#bl",
        'name_first': "Ethan",
        'name_last': "h",
    }
    user3_info = {
        'email': "Ethani@protonmail.com",
        'password': "aD1#bl",
        'name_first': "Ethan",
        'name_last': "i",
    }
    user_s = requests.post(f"{url}auth/register/v2", json=user1_info).json()
    user_h = requests.post(f"{url}auth/register/v2", json=user2_info).json()
    user_i = requests.post(f"{url}auth/register/v2", json=user3_info).json()
    channel_join(user_s, channel_id)
    requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': '@ethans @ethans hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii',
    })
    response = requests.get(f"{url}notifications/get/v1", params={
        'token': user_s['token']
    }).json()
    assert len(response['notifications']) == 1
    channel_join(user_h, channel_id)
    channel_join(user_i, channel_id)
    requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': '@ethans @ethanh hi@ethans',
    })
    requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': '@ethans 1',
    })
    response1 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_s['token']
    }).json()
    assert len(response1['notifications']) == 3
    response2 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_h['token']
    }).json()
    assert len(response2['notifications']) == 1

    # DM send notifications
    res = requests.post(f"{url}dm/create/v1", json={
        'token': user_s['token'],
        'u_ids': [user_h['auth_user_id']],
    }).json()
    dm_id1 = res['dm_id']
    requests.post(f"{url}message/senddm/v1", json={
        'token': user_s['token'],
        'dm_id': dm_id1,
        'message': "@ethanh hi@ethanh @ethans",
    })
    response3 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_s['token']
    }).json()
    response4 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_h['token']
    }).json()
    assert len(response3['notifications']) == 4
    assert len(response4['notifications']) == 3

    for _i in range(10):
        send_message(user_s, channel_id)
    response5 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_i['token']
    }).json()
    assert len(response5['notifications']) == 10
    for _i in range(30):
        send_message(user_s, channel_id)
    response6 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_i['token']
    }).json()
    assert len(response6['notifications']) == 20

def test_message_react_notifications(clear, user0, channel_id):
    user1_info = {
        'email': "Ethans@protonmail.com",
        'password': "aD1#bl",
        'name_first': "Ethan",
        'name_last': "s",
    }
    user2_info = {
        'email': "Ethanh@protonmail.com",
        'password': "aD1#bl",
        'name_first': "Ethan",
        'name_last': "h",
    }
    user_s = requests.post(f"{url}auth/register/v2", json=user1_info).json()
    user_h = requests.post(f"{url}auth/register/v2", json=user2_info).json()
    channel_join(user_s, channel_id)
    response1 = requests.post(f"{url}message/send/v1", json={
        'token': user_s['token'],
        'channel_id': channel_id,
        'message': 'hi!'
    }).json()
    message_id = response1['message_id']
    requests.post(f"{url}/message/react/v1",json={
        'token': user0['token'],
        'message_id': message_id,
        'react_id': 1})
    response2 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_s['token']
    }).json()
    assert len(response2['notifications']) == 1
    requests.post(f"{url}/message/react/v1",json={
        'token': user_s['token'],
        'message_id': message_id,
        'react_id': 1})
    response3 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_s['token']
    }).json()
    assert len(response3['notifications']) == 2

    # Dm react message notifications
    response4 = requests.post(f"{url}dm/create/v1", json={
        'token': user_s['token'],
        'u_ids': [user_h['auth_user_id']],
    }).json()
    response5 = requests.post(f"{url}message/senddm/v1", json={
        'token': user_h['token'],
        'dm_id': response4['dm_id'],
        'message': "hiiiiii",
    }).json()
    requests.post(f"{url}/message/react/v1",json={
        'token': user_s['token'],
        'message_id': response5['message_id'],
        'react_id': 1})
    response6 = requests.get(f"{url}notifications/get/v1", params={
        'token': user_h['token']
    }).json()
    assert len(response6['notifications']) == 2
    
def channel_join(user,channel_id):
    """
    User join the channel with channel_id
    """
    requests.post(f"{url}channel/join/v2", json={
        'token': user['token'], 
        'channel_id': channel_id,
    }).json()

def send_message(user, channel_id):
    """
    Send the message and return message_id
    """
    response = requests.post(f"{url}message/send/v1", json={
        'token': user['token'],
        'channel_id': channel_id,
        'message': '@ethani hi@ethani'
    }).json()
    return response['message_id']