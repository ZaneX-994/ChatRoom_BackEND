import pytest
import requests
from src.config import url
from src.error import InputError, AccessError

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
def new_tokn_and_ch_id(three_new_sample_users):
    ch_id = requests.post(f"{url}channels/create/v2", json={
        'token': three_new_sample_users['sample_token_0'],
        'name': 'New Channel',
        'is_public': True
    }).json()['channel_id']
    return {
        'tokn': three_new_sample_users['sample_token_0'],
        'ch_id': ch_id,
        'uid': three_new_sample_users['sample_uid_0'],
    }

# Given a valid channel_id, tests that two valid users' tokens can 
# successfully join a channel 
def test_2_users_leave_owners_channel(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    teacher = new_tokn_and_ch_id['tokn']
    school_ch_id = new_tokn_and_ch_id['ch_id']
    
    # users join channel
    student_1 = three_new_sample_users['sample_token_1']
    student_2 = three_new_sample_users['sample_token_2']
    requests.post(f"{url}channel/join/v2", json={
        'token': student_1, 'channel_id': school_ch_id,
    })
    requests.post(f"{url}channel/join/v2", json={
        'token': student_2, 'channel_id': school_ch_id,
    })
    members = requests.get(f"{url}channel/details/v2", params={
        'token': teacher, 'channel_id': school_ch_id, 
    }).json()['all_members']
    assert len(members) == 3

    # 1 user leaves channel
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': student_1, 'channel_id': school_ch_id,
    }) 
    assert response.status_code == 200
    members = requests.get(f"{url}channel/details/v2", params={
        'token': teacher, 'channel_id': school_ch_id, 
    }).json()['all_members']
    assert len(members) == 2
    
    # 2nd user leaves channel
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': student_2, 'channel_id': school_ch_id,
    }) 
    assert response.status_code == 200
    members = requests.get(f"{url}channel/details/v2", params={
        'token': teacher, 'channel_id': school_ch_id, 
    }).json()['all_members']
    assert len(members) == 1

# Tests if channel_id does not refer to a valid, existing channel
def test_nonexistant_channel_id(reset_data_store, new_tokn_and_ch_id):
    valid_token = new_tokn_and_ch_id['tokn']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    current_channels = requests.get(f"{url}channels/listall/v2", params={
        'token': valid_token,
    }).json()['channels']
    assert len(current_channels) == 1       # one channel exists...
    assert current_channels[0]['channel_id'] == valid_ch_id
    assert current_channels[0]['name'] == 'New Channel'
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': valid_token, 'channel_id': valid_ch_id+1,
    }) 
    assert response.status_code == InputError.code

# Tests if the only channel owner leaves, the channel will remain
def test_owner_leaves_channel(reset_data_store, new_tokn_and_ch_id):
    valid_token = new_tokn_and_ch_id['tokn'] 
    valid_uid = new_tokn_and_ch_id['uid'] 
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    current_channels = requests.get(f"{url}channels/listall/v2", params={
        'token': valid_token,
    }).json()['channels']
    assert len(current_channels) == 1       # one channel exists...
    assert current_channels[0]['channel_id'] == valid_ch_id
    assert current_channels[0]['name'] == 'New Channel'
    ch_dets_before = requests.get(f"{url}channel/details/v2", params={
        'token': valid_token, 'channel_id': valid_ch_id, 
    }).json()
    owners_before = ch_dets_before['owner_members']
    members_before = ch_dets_before['all_members']
    assert len(owners_before) == 1
    assert len(members_before) == len(owners_before)
    assert members_before == owners_before
    print(f'{owners_before} sdkjhkfjsdhkfh')
    assert valid_uid == owners_before[0]['u_id']

    # Owner leaves
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': valid_token, 'channel_id': valid_ch_id,
    }) 
    assert response.status_code == 200

    # The channel should still exist...
    requests.get(f"{url}channels/listall/v2", params={
        'token': valid_token,
    }).json()['channels']
    assert len(current_channels) == 1
    assert current_channels[0]['channel_id'] == valid_ch_id
    assert current_channels[0]['name'] == 'New Channel'

# Test that unregistered tokens can't be used to leave an existing channel
def test_unregistered_token(reset_data_store, new_tokn_and_ch_id):
    bad_token = new_tokn_and_ch_id['tokn'] + 'Uxf'
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': bad_token, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code

# Test that a nonmember's token can't be used to leave a channel
def test_non_member_token(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    non_member = three_new_sample_users['sample_token_1']
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': non_member, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code

# Tests with invalid token data types
def test_invalid_token_types(reset_data_store, new_tokn_and_ch_id):
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': 20.434, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': 65.76854**2, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': True, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': False, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': [], 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': {}, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': (), 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code

# Tests with invalid channel id data types
def test_invalid_channel_id_types(reset_data_store, new_tokn_and_ch_id):
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': 85435.4,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': 454.75424**2,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': True,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': False,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': [],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': {},
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': (),
    })
    assert response.status_code == InputError.code

# Tests return is an empty dictionary
def test_returns_empty_dict(reset_data_store, new_tokn_and_ch_id):
    ret = requests.post(f"{url}channel/leave/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert ret.status_code == 200
    assert ret.json() == {}
