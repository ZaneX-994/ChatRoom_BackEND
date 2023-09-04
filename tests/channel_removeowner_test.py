import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME
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
        "email": "b@example.com",
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }

@pytest.fixture
def userThree():
    return {
        "email": "c@example.com",
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }

# test remove with invalid channel_id
def test_with_invalid_channel_id(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()
    remove_result = requests.post(f"{url}channel/removeowner/v1", json={
        'token': register_result['token'],
        'channel_id': 100,
        'u_id': register_result['auth_user_id'],
    })

    assert remove_result.status_code == InputError.code

# test remove with invalid u_id
def test_with_invalid_uid(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()
    channels_create_result = requests.post(f"{url}channels/create/v2", json={
        'token': register_result['token'],
        'name': 'ChannelOne',
        'is_public': True
    }).json()
    remove_result = requests.post(f"{url}channel/removeowner/v1", json={
        'token': register_result['token'],
        'channel_id': channels_create_result['channel_id'],
        'u_id': register_result['auth_user_id'] + 1,
    })

    assert remove_result.status_code == InputError.code

# test remove with invalidate token
def test_with_invalidate_token(reset, userOne):
    register_result = requests.post(f"{url}auth/register/v2", json=userOne).json()
    channels_create_result = requests.post(f"{url}channels/create/v2", json={
        'token': register_result['token'],
        'name': 'ChannelOne',
        'is_public': True
    }).json()

    remove_result = requests.post(f"{url}channel/removeowner/v1", json={
        'token': f"{register_result['token']}123",
        'channel_id': channels_create_result['channel_id'],
        'u_id': register_result['auth_user_id'],
    })

    assert remove_result.status_code == AccessError.code

# test owner can not be removed by a normal member
def test_member_cant_remove_owner(reset, userOne, userTwo, userThree):
    userOne_registion = requests.post(f"{url}auth/register/v2", json=userOne).json()
    channels_create_result = requests.post(f"{url}channels/create/v2", json={
        'token': userOne_registion['token'],
        'name': 'ChannelOne',
        'is_public': True,
    }).json()

    userTwo_registion = requests.post(f"{url}auth/register/v2", json=userTwo).json()
    requests.post(f"{url}channel/join/v2", json={
        'token': userTwo_registion['token'],
        'channel_id': channels_create_result['channel_id'],
    })

    userThree_registion = requests.post(f"{url}auth/register/v2", json=userThree).json()
    requests.post(f"{url}channel/join/v2", json={
        'token': userThree_registion['token'],
        'channel_id': channels_create_result['channel_id'],
    })

    requests.post(f"{url}channel/addowner/v2", json={
        'token': userThree_registion['token'],
        'channel_id': channels_create_result['channel_id'],
        'u_id': userThree_registion['auth_user_id'],
    }) 

    remove_result = requests.post(f"{url}channel/removeowner/v1", json={
        'token': userTwo_registion['token'],
        'channel_id': channels_create_result['channel_id'],
        'u_id': userOne_registion['auth_user_id'],
    })

    assert remove_result.status_code == AccessError.code
# test cant remove the only owner of the channel
def test_with_one_owner(reset, userOne, userTwo):
    userOne_registion = requests.post(f"{url}auth/register/v2", json=userOne).json()
    userTwo_registion = requests.post(f"{url}auth/register/v2", json=userTwo).json()
    channels_create_result = requests.post(f"{url}channels/create/v2", json={
        'token': userTwo_registion['token'],
        'name': 'ChannelOne',
        'is_public': True,
    }).json()
    requests.post(f"{url}channel/join/v2", json={
        'token': userOne_registion['token'],
        'channel_id': channels_create_result['channel_id'],
    })
    remove_result = requests.post(f"{url}channel/removeowner/v1", json={
        'token': userOne_registion['token'],
        'channel_id': channels_create_result['channel_id'],
        'u_id': userTwo_registion['auth_user_id'],
    })

    assert remove_result.status_code == InputError.code

# test remove success
def test_with_sucess(reset, userOne, userTwo):
    userOne_registion = requests.post(f"{url}auth/register/v2", json=userOne).json()
    userTwo_registion = requests.post(f"{url}auth/register/v2", json=userTwo).json()
    channels_create_result = requests.post(f"{url}channels/create/v2", json={
        'token': userOne_registion['token'],
        'name': 'ChannelOne',
        'is_public': True,
    }).json()
    requests.post(f"{url}channel/join/v2", json={
        'token': userTwo_registion['token'],
        'channel_id': channels_create_result['channel_id'],
    })

    requests.post(f"{url}channel/addowner/v2", json={
        'token': userOne_registion['token'],
        'channel_id': channels_create_result['channel_id'],
        'u_id': userTwo_registion['auth_user_id'],
    }) 
    
    remove_result = requests.post(f"{url}channel/removeowner/v1", json={
        'token': userOne_registion['token'],
        'channel_id': channels_create_result['channel_id'],
        'u_id': userTwo_registion['auth_user_id'],
    })

    assert remove_result.status_code == 200

# test with non exist channel_id
def test_non_exist_channel_id(reset, userOne, userTwo):
    userOne_registion = requests.post(f"{url}auth/register/v2", json=userOne).json()
    userTwo_registion = requests.post(f"{url}auth/register/v2", json=userTwo).json()
    channels_create_result = requests.post(f"{url}channels/create/v2", json={
        'token': userOne_registion['token'],
        'name': 'ChannelOne',
        'is_public': True,
    }).json()
    requests.post(f"{url}channel/join/v2", json={
        'token': userTwo_registion['token'],
        'channel_id': channels_create_result['channel_id'],
    })

    requests.post(f"{url}channel/addowner/v2", json={
        'token': userOne_registion['token'],
        'channel_id': channels_create_result['channel_id'],
        'u_id': userTwo_registion['auth_user_id'],
    }) 
    
    remove_result = requests.post(f"{url}channel/removeowner/v1", json={
        'token': userOne_registion['token'],
        'channel_id': channels_create_result['channel_id'] + 1,
        'u_id': userTwo_registion['auth_user_id'],
    })

    assert remove_result.status_code == InputError.code
