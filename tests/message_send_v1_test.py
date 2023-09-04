import pytest
from src.config import url
import requests
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from tests.dm_create_test import user0, user1

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

def test_invalid_length_long(clear, user0, channel_id):
    response = requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'hi' * 1000,
    })
    assert response.status_code == 400

def test_invalid_length_short(clear, user0, channel_id):
    response = requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': '',
    })
    assert response.status_code == 400

# user is not channel member
def test_invalid_user(clear, user0, user1, channel_id):
    response = requests.post(f"{url}message/send/v1", json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'hi',
    })
    assert response.status_code == 403

def test_invalid_channel_id(clear, user0):
    response = requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': 4,
        'message': 'hi',
    })
    assert response.status_code == 400

def test_invlid_token(clear, user0, channel_id):
    response = requests.post(f"{url}message/send/v1", json={
        'token': '1',
        'channel_id': channel_id,
        'message': 'hi',
    })
    assert response.status_code == 403

def test_message_send(clear, user0, channel_id):
    response = requests.post(f"{url}message/send/v1", json={
        'token': user0['token'],
        'channel_id': channel_id,
        'message': 'hi',
    }).json()
    assert 'message_id' in response