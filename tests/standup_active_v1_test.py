import pytest
import requests
from src.config import url
from src.error import InputError, AccessError
import time

SAMPLE_STDUP_LEN = 3 #seconds

@pytest.fixture
def reset_data_store():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def three_new_sample_users():
    u_0_info = {
        'email': "joe.shmoe@protonmail.com",
        'password': "aD1#bl",
        'name_first': "Joe",
        'name_last': "Shmoe",
    }
    u_1_info = {
        'email': "donkey.kong78@outlook.com",
        'password': "banana",
        'name_first': "Donkey",
        'name_last': "Kong",
    }
    u_2_info = {
        'email': "bg@gmail.com",
        'password': "A|1ve!",
        'name_first': "Bee",
        'name_last': "Gees",
    }
    response_0 = requests.post(f"{url}auth/register/v2", json=u_0_info)
    response_1 = requests.post(f"{url}auth/register/v2", json=u_1_info)
    response_2 = requests.post(f"{url}auth/register/v2", json=u_2_info)
    assert response_0.status_code == 200
    assert response_1.status_code == 200
    assert response_2.status_code == 200
    new_usr_0 = response_0.json()
    new_usr_1 = response_1.json()
    new_usr_2 = response_2.json()
    assert 'token' in new_usr_0
    assert 'token' in new_usr_1
    assert 'token' in new_usr_2
    assert 'auth_user_id' in new_usr_0
    assert 'auth_user_id' in new_usr_1
    assert 'auth_user_id' in new_usr_2
    assert type(new_usr_0['token']) == str
    assert type(new_usr_1['token']) == str
    assert type(new_usr_2['token']) == str
    assert type(new_usr_0['auth_user_id']) == int
    assert type(new_usr_1['auth_user_id']) == int
    assert type(new_usr_2['auth_user_id']) == int
    # there are 3 valid users in the data_store now^
    sample_usrs = {
        'sample_token_0': new_usr_0['token'],
        'sample_uid_0': new_usr_0['auth_user_id'],
        'sample_token_1': new_usr_1['token'],
        'sample_uid_1': new_usr_1['auth_user_id'],
        'sample_token_2': new_usr_2['token'],
        'sample_uid_2': new_usr_2['auth_user_id'],
    }
    return sample_usrs

@pytest.fixture
def new_channel(three_new_sample_users):
    token = three_new_sample_users['sample_token_0']
    ch_id = requests.post(f"{url}channels/create/v2", json={
        'token': token, 'name': 'New Channel', 'is_public': True
    }).json()['channel_id']
    return {
        'creator_token': token,
        'ch_id': ch_id,
    }


# Tests a valid scenario that should have standup/active/v1
# return { 'is_active': True, 'time_finish': <valid length in seconds> }
def test_standup_active(reset_data_store, new_channel):
    # The channel has just been created; let standup/start/v1 be called...
    time_stdup_started = time.time()
    response = requests.post(f"{url}standup/start/v1", json={
        'token': new_channel['creator_token'],
        'channel_id': new_channel['ch_id'],
        'length': SAMPLE_STDUP_LEN,
    })
    response = requests.get(f"{url}standup/active/v1", params={
        'token': new_channel['creator_token'],
        'channel_id': new_channel['ch_id'],
    })
    assert response.status_code == 200
    standup_info = response.json()
    assert type(standup_info) == dict
    assert len(standup_info) == 2
    assert 'is_active' in standup_info
    assert 'time_finish' in standup_info
    assert standup_info['is_active'] == True
    stdup_timing_diff = standup_info['time_finish'] - (time_stdup_started + SAMPLE_STDUP_LEN) 
    assert abs(stdup_timing_diff) <= 1

# Tests a valid scenario that should have standup/active/v1
# return { 'is_active': False, 'time_finish': None }
def test_no_standup_active(reset_data_store, new_channel):
    # The channel has just been created; standup/start/v1 has not been called...
    response = requests.get(f"{url}standup/active/v1", params={
        'token': new_channel['creator_token'],
        'channel_id': new_channel['ch_id'],
    })
    assert response.status_code == 200 # ...this is okay...
    standup_info = response.json()
    assert standup_info == {'is_active': False, 'time_finish': None}
    # ...it just means that this^^^ is the return.


# Tests whether a token parameter unknown to the server makes
# standup/active/v1 return an AccessError
def test_unregistered_token(reset_data_store, three_new_sample_users, new_channel):
    response = requests.get(f"{url}standup/active/v1", params={
        'token': three_new_sample_users['sample_token_0'] + 'ds32s',
        'channel_id': new_channel['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}standup/active/v1", params={
        'token': three_new_sample_users['sample_token_1'] + '435m',
        'channel_id': new_channel['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}standup/active/v1", params={
        'token': three_new_sample_users['sample_token_2'] + '32*',
        'channel_id': new_channel['ch_id'],
    })
    assert response.status_code == AccessError.code

# Tests whether a token parameter unknown to the server makes
# standup/active/v1 return an InputError
def test_nonexistant_channel_id(reset_data_store, new_channel):
    # Registered token passed in, but no channel with id == (new_channel['ch_id'] + 5) exists yet:
    response = requests.get(f"{url}standup/active/v1", params={
        'token': new_channel['creator_token'],
        'channel_id': new_channel['ch_id'] + 5,
    })
    assert response.status_code == InputError.code
    
# Test that a nonmember's token can't be used to check the channel's standup info
def test_non_member_token(reset_data_store, three_new_sample_users, new_channel):
    non_member = three_new_sample_users['sample_token_1']
    print(non_member)
    print(str(new_channel['ch_id'])+ '\n\n\n')
    response = requests.get(f"{url}standup/active/v1", params={
        'token': non_member,
        'channel_id': new_channel['ch_id'],
    })
    assert response.status_code == AccessError.code