import pytest
import requests
from src.config import url
from src.error import InputError, AccessError

@pytest.fixture
def reset_datastore():
    requests.delete(f"{url}clear/v1")

# Helper function to create sample users with 
# valid tokens and user ids.
@pytest.fixture
def three_new_sample_users():
    u_0_info = {
        'email': "a@example.com",
        'password': "password",
        'name_first': "John",
        'name_last': "Doe",
    }
    u_1_info = {
        'email': "j@example.com",
        'password': "pass123",
        'name_first': "Jack",
        'name_last': "Smith",
    }
    u_2_info = {
        'email': "donkey.kong78@outlook.com",
        'password': "banana",
        'name_first': "Donkey",
        'name_last': "Kong",
    }

    response_0 = requests.post(f"{url}auth/register/v2", json = u_0_info)
    response_1 = requests.post(f"{url}auth/register/v2", json = u_1_info)
    response_2 = requests.post(f"{url}auth/register/v2", json = u_2_info)

    assert response_0.status_code == 200
    assert response_1.status_code == 200
    assert response_2.status_code == 200

    new_user_0 = response_0.json()
    new_user_1 = response_1.json()
    new_user_2 = response_2.json()
    
    assert 'token' in new_user_0
    assert 'token' in new_user_1
    assert 'token' in new_user_2

    assert 'auth_user_id' in new_user_0
    assert 'auth_user_id' in new_user_1
    assert 'auth_user_id' in new_user_2

    assert type(new_user_0['token']) == str
    assert type(new_user_1['token']) == str
    assert type(new_user_2['token']) == str
    
    assert type(new_user_0['auth_user_id']) == int
    assert type(new_user_1['auth_user_id']) == int
    assert type(new_user_2['auth_user_id']) == int
    
    # 3 Valid users in the datastore at the moment
    sample_users = {
        'sample_token_0': new_user_0['token'],
        'sample_uid_0': new_user_0['auth_user_id'],

        'sample_token_1': new_user_1['token'],
        'sample_uid_1': new_user_1['auth_user_id'],

        'sample_token_2': new_user_2['token'],
        'sample_uid_2': new_user_2['auth_user_id'],
    }
    return sample_users

# Test case for successfully inviting a user to a channel
def test_channel_invite_v2_successful(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                    'name': 'newChannel', 'is_public': False}).json()
    response = requests.post(f"{url}channel/invite/v2", 
                        json={'token': three_new_sample_users['sample_token_0'], 
                        'channel_id': new_channel['channel_id'],
                        'u_id': three_new_sample_users['sample_uid_1']})
    assert response.status_code == 200

# Test case for a channel_id not referring to a valid channel ~ raise InputError
def test_channel_invite_v2_invalid_channel_id(reset_datastore, three_new_sample_users):
    response = requests.post(f"{url}channel/invite/v2", 
                        json={'token': three_new_sample_users['sample_token_0'], 
                        'channel_id': 'new@1',
                        'u_id': three_new_sample_users['sample_uid_1']})
    assert response.status_code == InputError.code

# Test case for a u_id not referring to a valid user ~ raise InputError
def test_channel_invite_v2_ivalid_user_u_id(reset_datastore, three_new_sample_users): 
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                    'name': 'newChannel', 'is_public': False}).json()
    response = requests.post(f"{url}channel/invite/v2",
                                json={'token': three_new_sample_users['sample_token_0'],
                                'channel_id': new_channel['channel_id'],
                                'u_id': 'inv_uid'})
    assert response.status_code == InputError.code

# Test case for a u_id referring to a valid member of the channel ~ raise InputError
def test_channel_invite_v2_existing_user(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2",
                                json = {'token': three_new_sample_users['sample_token_0'],
                                        'name': 'newChannel', 'is_public': False}).json()
    requests.post(f"{url}channel/invite/v2",
                    json={'token': three_new_sample_users['sample_token_0'],
                    'channel_id': new_channel['channel_id'],
                    'u_id': three_new_sample_users['sample_uid_1']})
    response_2 = requests.post(f"{url}channel/invite/v2",
                                json={'token': three_new_sample_users['sample_token_0'],
                                'channel_id': new_channel['channel_id'],
                                'u_id': three_new_sample_users['sample_uid_1']})
    assert response_2.status_code == InputError.code

# Test case for a non-channel-member inviting a user to a valid channel ~ raise AccessError
def test_channel_invite_v2_auth_id_not_member(reset_datastore, three_new_sample_users):    
    new_channel = requests.post(f"{url}channels/create/v2",
                                json = {'token': three_new_sample_users['sample_token_0'],
                                        'name': 'newChannel', 'is_public': False}).json()
    response = requests.post(f"{url}channel/invite/v2",
                                json={'token': three_new_sample_users['sample_token_2'],
                                'channel_id': new_channel['channel_id'],
                                'u_id': three_new_sample_users['sample_uid_1']})
    assert response.status_code == AccessError.code
