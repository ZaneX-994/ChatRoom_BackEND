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
    tokn = three_new_sample_users['sample_token_0']
    ch_id = requests.post(f"{url}channels/create/v2", json={
        'token': tokn, 'name': 'New Channel', 'is_public': True
    }).json()['channel_id']
    return {
        'tokn': tokn,
        'ch_id': ch_id,
    }

# Given a valid channel_id, tests that two valid users' tokens can 
# successfully join a channel 
def test_users_joins_new_public_channel(reset_data_store, three_new_sample_users):
    # Have first user make a channel, and that they are it's only member:
    teacher = three_new_sample_users['sample_token_0']
    teacher_id = three_new_sample_users['sample_uid_0']
    school_channel = requests.post(f"{url}channels/create/v2", json={
        'token': teacher, 'name': 'School', 'is_public': True
    }).json()['channel_id']
    assert type(school_channel) == int
    result = requests.get(f"{url}channels/listall/v2", params={
        'token': teacher
    }).json()['channels'][0]
    assert result['channel_id'] == school_channel
    assert result['name'] == 'School'
    school_ch_members_1 = requests.get(f"{url}channel/details/v2", params={
        'token': teacher, 'channel_id': school_channel, 
    }).json()['all_members']
    # print(f'{school_ch_members_1}' '<><><><><')
    assert type(school_ch_members_1) == list
    assert len(school_ch_members_1) == 1  
    assert school_ch_members_1[0]['u_id'] == teacher_id

    # Now a second user will join the 'School' channel, becoming its second member:
    student_1 = three_new_sample_users['sample_token_1']
    student_1_id = three_new_sample_users['sample_uid_1']
    ch_join_ret = requests.post(f"{url}channel/join/v2", json={
        'token': student_1, 'channel_id': school_channel,
    })
    assert ch_join_ret.status_code == 200
    assert ch_join_ret.json() == {}
    school_ch_members_2 = requests.get(f"{url}channel/details/v2", params={
        'token': student_1, 'channel_id': school_channel, 
    }).json()['all_members']
    assert type(school_ch_members_2) == list
    assert len(school_ch_members_2) == 2  
    assert school_ch_members_2[0]['u_id'] == teacher_id
    assert school_ch_members_2[1]['u_id'] == student_1_id

    # Now a second user will join the 'School' channel, becoming its second member:
    student_2 = three_new_sample_users['sample_token_2']
    student_2_id = three_new_sample_users['sample_uid_2']
    ch_join_ret = requests.post(f"{url}channel/join/v2", json={
        'token': student_2, 'channel_id': school_channel,
    })
    assert ch_join_ret.status_code == 200
    assert ch_join_ret.json() == {}
    school_ch_members_3 = requests.get(f"{url}channel/details/v2", params={
        'token': student_2, 'channel_id': school_channel, 
    }).json()['all_members']
    assert type(school_ch_members_3) == list
    assert len(school_ch_members_3) == 3
    assert school_ch_members_3[0]['u_id'] == teacher_id
    assert school_ch_members_3[1]['u_id'] == student_1_id
    assert school_ch_members_3[2]['u_id'] == student_2_id


# Test global owner joining a private channel created by someone else
def test_global_owner_joins_private_channel(reset_data_store, three_new_sample_users):
    # Global owner is first user registered.
    global_owner = three_new_sample_users['sample_token_0']
    global_owner_id = three_new_sample_users['sample_uid_0']
    student_1 = three_new_sample_users['sample_token_1']
    student_1_id = three_new_sample_users['sample_uid_1']
    school_channel = requests.post(f"{url}channels/create/v2", json={
        'token': student_1, 'name': 'General', 'is_public': False
    }).json()['channel_id']
    ch_join_ret = requests.post(f"{url}channel/join/v2", json={
        'token': global_owner, 'channel_id': school_channel,
    })
    assert ch_join_ret.status_code == 200
    assert ch_join_ret.json() == {}
    result = requests.get(f"{url}channel/details/v2", params={
        'token': global_owner, 'channel_id': school_channel, 
    }).json()['all_members']
    assert type(result) == list
    assert len(result) == 2
    assert result[0]['u_id'] == student_1_id
    assert result[1]['u_id'] == global_owner_id

# Requires channel_details_v1 to pass 
def test_user_tries_to_join_private_channel(reset_data_store, three_new_sample_users):
    # Have first user make a new private channel
    teacher = three_new_sample_users['sample_token_0']
    teacher_id = three_new_sample_users['sample_uid_0']
    staff_channel = requests.post(f"{url}channels/create/v2", json={
        'token': teacher, 'name': 'Staff', 'is_public': False
    }).json()['channel_id']
    assert type(staff_channel) == int
    result = requests.get(f"{url}channels/listall/v2", params={
        'token': teacher
    }).json()['channels'][0]
    assert result['channel_id'] == staff_channel
    assert result['name'] == 'Staff'
    staff_ch_members_before = requests.get(f"{url}channel/details/v2", params={
        'token': teacher, 'channel_id': staff_channel, 
    }).json()['all_members']
    assert type(staff_ch_members_before) == list
    assert len(staff_ch_members_before) == 1
    assert staff_ch_members_before[0]['u_id'] == teacher_id

    # Another user (even if they are registered) cannot join the private channel on their own:
    student_1 = three_new_sample_users['sample_token_1']
    ch_join_ret = requests.post(f"{url}channel/join/v2", json={
        'token': student_1, 'channel_id': staff_channel,
    })
    assert ch_join_ret.status_code == AccessError.code

    student_2 = three_new_sample_users['sample_token_2']
    ch_join_ret = requests.post(f"{url}channel/join/v2", json={
        'token': student_2, 'channel_id': staff_channel,
    })
    assert ch_join_ret.status_code == AccessError.code
    
    staff_ch_members_after = requests.get(f"{url}channel/details/v2", params={
        'token': teacher, 'channel_id': staff_channel, 
    }).json()['all_members']
    assert type(staff_ch_members_after) == list                 # Nothing should have changed here
    assert len(staff_ch_members_after) == 1                     #
    assert staff_ch_members_after == staff_ch_members_before    #

def test_nonexistant_channel_id(reset_data_store, three_new_sample_users):
    valid_token = three_new_sample_users['sample_token_0']
    current_channels = requests.get(f"{url}channels/listall/v2", params={
        'token': valid_token,
    }).json()['channels']
    assert len(current_channels) == 0       # no channels exist yet...
    response = requests.post(f"{url}channel/join/v2", json={
        'token': valid_token, 'channel_id': 0,
    })                                      #...meaning you can't join any! 
    assert response.status_code == InputError.code

def test_unregistered_token(reset_data_store, new_tokn_and_ch_id):
    bad_token = new_tokn_and_ch_id['tokn'] + 'Uxf'
    response = requests.post(f"{url}channel/join/v2", json={
        'token': bad_token, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code

def test_user_already_member(reset_data_store, three_new_sample_users):
    #channel creator can't join
    user_0 = three_new_sample_users['sample_token_0']
    new_channel = requests.post(f"{url}channels/create/v2", json={
        'token': user_0, 'name': 'New Channel', 'is_public': True
    }).json()['channel_id']
    ch_join_ret_code = requests.post(f"{url}channel/join/v2", json={
        'token': user_0, 'channel_id': new_channel,
    }).status_code
    assert ch_join_ret_code == InputError.code  # ^This shouldn't work!

    #the following two users also can't join twice
    user_1 = three_new_sample_users['sample_token_1']
    ch_join_ret_code = requests.post(f"{url}channel/join/v2", json={
        'token': user_1, 'channel_id': new_channel,
    }).status_code
    assert ch_join_ret_code == 200              # ^This should be fine
    ch_join_ret_code = requests.post(f"{url}channel/join/v2", json={
        'token': user_1, 'channel_id': new_channel,
    }).status_code
    assert ch_join_ret_code == InputError.code  # ^This shouldn't work!

    user_2 = three_new_sample_users['sample_token_2']
    ch_join_ret_code = requests.post(f"{url}channel/join/v2", json={
        'token': user_2, 'channel_id': new_channel,
    }).status_code
    assert ch_join_ret_code == 200              # ^This should be fine
    ch_join_ret_code = requests.post(f"{url}channel/join/v2", json={
        'token': user_2, 'channel_id': new_channel,
    }).status_code
    assert ch_join_ret_code == InputError.code  # ^This shouldn't work!

def test_invalid_token_types(reset_data_store, new_tokn_and_ch_id):
    response = requests.post(f"{url}channel/join/v2", json={
        'token': 20.434, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': 65.76854**2, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': True, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': False, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': [], 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': {}, 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': (), 'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert response.status_code == AccessError.code

def test_invalid_channel_id_types(reset_data_store, new_tokn_and_ch_id):
    response = requests.post(f"{url}channel/join/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': 85435.4,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': 454.75424**2,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': True,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': False,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': [],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': {},
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/join/v2", json={
        'token': new_tokn_and_ch_id['tokn'], 'channel_id': (),
    })
    assert response.status_code == InputError.code

def test_returns_empty_dict(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    ret = requests.post(f"{url}channel/join/v2", json={
        'token': three_new_sample_users['sample_token_1'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
    })
    assert ret.status_code == 200
    assert ret.json() == {}

def test_empty_data_store(reset_data_store): 
    code = requests.post(f"{url}channel/join/v2", json={
        'token': 'donkey', 'channel_id': 0,
    }).status_code
    assert code == AccessError.code
