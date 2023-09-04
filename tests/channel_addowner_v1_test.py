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

def test_adding_of_two_new_owners(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    valid_invitor_token = new_tokn_and_ch_id['tokn']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    valid_invitee_id_1 = three_new_sample_users['sample_uid_1']
    valid_invitee_id_2 = three_new_sample_users['sample_uid_2']
    valid_invitee_token_1 = three_new_sample_users['sample_token_1']
    valid_invitee_token_2 = three_new_sample_users['sample_token_2']
    # channel creator should be only owner
    owners_list = requests.get(f"{url}channel/details/v2", params={
        'token': valid_invitor_token, 'channel_id': valid_ch_id, 
    }).json()['owner_members']
    assert len(owners_list) == 1
    
    # make first user an member of the channel...
    requests.post(f"{url}channel/join/v2", json={
        'token': valid_invitee_token_1, 'channel_id': valid_ch_id,
    })
    # ... and then make them an owner
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': valid_invitor_token,
        'channel_id': valid_ch_id,
        'u_id': valid_invitee_id_1,
    })
    assert response.status_code == 200
    assert response.json() == {}
    # # There should now be two owners now
    owners_list = requests.get(f"{url}channel/details/v2", params={
        'token': valid_invitor_token, 'channel_id': valid_ch_id, 
    }).json()['owner_members']
    assert len(owners_list) == 2

    # make second user an member of the channel...
    requests.post(f"{url}channel/join/v2", json={
        'token': valid_invitee_token_2, 'channel_id': valid_ch_id,
    })
    # ... and then make them an owner
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': valid_invitor_token,
        'channel_id': valid_ch_id,
        'u_id': valid_invitee_id_2,
    })
    assert response.status_code == 200
    assert response.json() == {}
    # # There should now be three owners now
    owners_list = requests.get(f"{url}channel/details/v2", params={
        'token': valid_invitor_token, 'channel_id': valid_ch_id, 
    }).json()['owner_members']
    assert len(owners_list) == 3
    

def test_nonexistant_channel_id(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    valid_invitor_token = new_tokn_and_ch_id['tokn']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    valid_invitee_id = three_new_sample_users['sample_uid_1']
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': valid_invitor_token,
        'channel_id': valid_ch_id+1,
        'u_id': valid_invitee_id,
    })                                      
    assert response.status_code == InputError.code

def test_unregistered_token(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    bad_invitor_token = new_tokn_and_ch_id['tokn'] + 'Uxf'
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    valid_invitee_id = three_new_sample_users['sample_uid_1']
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': bad_invitor_token,
        'channel_id': valid_ch_id+1,
        'u_id': valid_invitee_id,
    })                                      
    assert response.status_code == AccessError.code

def test_unregistered_new_user(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    valid_invitor_token = new_tokn_and_ch_id['tokn']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    unregistered_uid = three_new_sample_users['sample_uid_1']*20

    # Try add a non-channel-member the channel's list of owners
    response = requests.post(f"{url}channel/addowner/v2", json={   #But this shouldn't work! 
        'token': valid_invitor_token,                               #
        'channel_id': valid_ch_id,                                  #
        'u_id': unregistered_uid,                                   #
    })                                                              #
    assert response.status_code == InputError.code                  #

def test_non_owner_attempt_to_add_new_user(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    unauthorised_adder_token = three_new_sample_users['sample_token_1']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    registered_uid = three_new_sample_users['sample_uid_2']

    # Try add a non-channel-member the channel's list of owners
    response = requests.post(f"{url}channel/addowner/v2", json={    #But this shouldn't work! 
        'token': unauthorised_adder_token,                          #
        'channel_id': valid_ch_id,                                  #
        'u_id': registered_uid,                                     #
    })                                                              #
    assert response.status_code == AccessError.code                  #

def test_user_is_not_a_member(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    valid_invitor_token = new_tokn_and_ch_id['tokn']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    non_member = three_new_sample_users['sample_uid_1']

    # Try add a non-channel-member the channel's list of owners
    response = requests.post(f"{url}channel/addowner/v2", json={   #But this shouldn't work! 
        'token': valid_invitor_token,                               #
        'channel_id': valid_ch_id,                                  #
        'u_id': non_member,                                         #
    })                                                              #
    assert response.status_code == InputError.code                  #

def test_user_is_already_owner(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    valid_invitor_token = new_tokn_and_ch_id['tokn']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    valid_invitee_id = three_new_sample_users['sample_uid_1']
    valid_invitee_token = three_new_sample_users['sample_token_1']
    
    # make a user an member of the channel...
    requests.post(f"{url}channel/join/v2", json={
        'token': valid_invitee_token, 'channel_id': valid_ch_id,
    })
    # ... and then make them an owner
    response = requests.post(f"{url}channel/addowner/v2", json={   #This should be fine... 
        'token': valid_invitor_token,                               #
        'channel_id': valid_ch_id,                                  #
        'u_id': valid_invitee_id,                                   #
    })                                                              #
    assert response.status_code == 200                              #

    # try to add them again
    response = requests.post(f"{url}channel/addowner/v2", json={   #... but this shouldn't work! 
        'token': valid_invitor_token,                               #
        'channel_id': valid_ch_id,                                  #
        'u_id': valid_invitee_id,                                   #
    })                                                              #
    assert response.status_code == InputError.code                  #

def test_owner_is_already_owner(reset_data_store, new_tokn_and_ch_id):
    valid_invitor_token = new_tokn_and_ch_id['tokn']
    valid_ch_id = new_tokn_and_ch_id['ch_id']
    bad_invitee_id = new_tokn_and_ch_id['uid']

    response = requests.post(f"{url}channel/addowner/v2", json={   #... but this shouldn't work! 
        'token': valid_invitor_token,                               #
        'channel_id': valid_ch_id,                                  #
        'u_id': bad_invitee_id,                                     #
    })                                                              #
    assert response.status_code == InputError.code                  #

def test_invalid_token_types(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': 20.434,
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': 65.76854**2,
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': True,
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': False,
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': [],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': {},
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == AccessError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': (),
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == AccessError.code

def test_invalid_ch_id_types(reset_data_store, three_new_sample_users, new_tokn_and_ch_id):
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': 85435.4,
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': 454.75424**2,
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': True,
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': False,
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': [],
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': {},
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': (),
        'u_id': three_new_sample_users['sample_uid_1'],
    })
    assert response.status_code == InputError.code

def test_invalid_u_id_types(reset_data_store, new_tokn_and_ch_id):
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': 85435.4,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': 454.75424**2,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': True,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': False,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': [],
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': {},
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}channel/addowner/v2", json={
        'token': new_tokn_and_ch_id['tokn'],
        'channel_id': new_tokn_and_ch_id['ch_id'],
        'u_id': (),
    })
    assert response.status_code == InputError.code
