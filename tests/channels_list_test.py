import pytest
import requests

from src.config import url
from src.error import InputError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME
from src.error import AccessError, InputError

@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def userOne():
    return {
        "email": VALID_EMAIL,
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }

@pytest.fixture
def userTwo():
    return {
        "email": "a" + VALID_EMAIL,
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }

# test when userOne is in no channel
def test_zero_channel(reset, userOne, userTwo):
    register_result1 = requests.post(f"{url}auth/register/v2", json=userOne).json()
    register_result2 = requests.post(f"{url}auth/register/v2", json=userTwo).json()

    token1 = register_result1['token']
    token2 = register_result2['token']
    
    requests.post(f"{url}channels/create/v2", json={
        'token': token2,
        'name': 'ChannelOne',
        'is_public': True,
    }).json()
    list_result = requests.get(f"{url}channels/list/v2", params={'token': token1})

    assert list_result.json()['channels'] == []
    assert list_result.status_code == 200

# test when userOne is in one channel
def test_channel_list_with_one_channel(reset, userOne, userTwo):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()
    token = register_result['token']

    channel_create_result = requests.post(f"{url}channels/create/v2", json={
        'token': token,
        'name': 'ChannelOne',
        'is_public': True,
    }).json()

    # Add another user to channel.
    token_two = requests.post(f"{url}auth/register/v2", json=userTwo).json()['token']
    requests.post(f"{url}channel/join/v2", json={
        'token': token_two, 
        'channel_id': channel_create_result['channel_id'],
    }).json()

    list_result = requests.get(f"{url}channels/list/v2", params={'token': token})

    assert list_result.json()['channels'][0]['name'] == 'ChannelOne'
    assert list_result.json()['channels'][0]['channel_id'] == channel_create_result['channel_id']
    assert list_result.status_code == 200

# test when token is invalid
def test_with_invalid_token(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()

    token = register_result['token']

    requests.post(f"{url}channels/create/v2", json={
        'token': token,
        'name': 'ChannelOne',
        'is_public': True,
    })

    list_result = requests.get(f"{url}channels/list/v2", params={'token': f"{token}123"})
    
    assert list_result.status_code == AccessError.code

# test when userOne is in multiple channels
def test_with_multiple_channels(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()

    token = register_result['token']

    requests.post(f"{url}channels/create/v2", json={
        'token': token,
        'name': 'ChannelOne',
        'is_public': True,
    })

    requests.post(f"{url}channels/create/v2", json={
        'token': token,
        'name': 'ChannelTwo',
        'is_public': True,
    })

    list_result = requests.get(f"{url}channels/list/v2", params={'token': f"{token}"})

    assert list_result.status_code == 200
    assert len(list_result.json()['channels']) == 2
