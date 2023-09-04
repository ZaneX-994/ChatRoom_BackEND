import pytest
import requests
from src.config import url
from src.error import AccessError

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
        'sample_handle_0': u_0_info['name_first'].lower() + u_0_info['name_last'].lower(),
        'sample_token_1': new_usr_1['token'],
        'sample_uid_1': new_usr_1['auth_user_id'],
        'sample_handle_1': u_1_info['name_first'].lower() + u_1_info['name_last'].lower(),
        'sample_token_2': new_usr_2['token'],
        'sample_uid_2': new_usr_2['auth_user_id'],
        'sample_handle_2': u_2_info['name_first'].lower() + u_2_info['name_last'].lower(),
    }
    return sample_usrs

# Tests whether a token parameter unknown to the server makes
# /dm/list/v1 return an AccessError
def test_unregistered_token(reset_data_store, three_new_sample_users):
    response = requests.get(f"{url}dm/list/v1", params={
        'token': three_new_sample_users['sample_token_0'] + 'Ndf'
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}dm/list/v1", params={
        'token': three_new_sample_users['sample_token_1'] + '435m'
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}dm/list/v1", params={
        'token': three_new_sample_users['sample_token_2'] + '32*'
    })
    assert response.status_code == AccessError.code

# Tests whether dm/list/v1 returns an 
# empty list if no dms have been created
def test_with_empty_channels(reset_data_store, three_new_sample_users):
    response_0 = requests.get(f"{url}dm/list/v1", params={
        'token': three_new_sample_users['sample_token_0']
    })
    response_1 = requests.get(f"{url}dm/list/v1", params={
        'token': three_new_sample_users['sample_token_1']
    })
    assert response_0.status_code == 200
    assert response_1.status_code == response_0.status_code
    assert type(response_0.json()['dms']) == list   
    assert response_0.json()['dms'] == []
    assert response_1.json()['dms'] == []

# Tests valid use of dm/list/v1 with the creation of two new dms
def test_with_a_pair_of_two_person_dms(reset_data_store, three_new_sample_users):
    me = three_new_sample_users['sample_token_0']
    my_hndl = three_new_sample_users['sample_handle_0']
    # No dms exist yet
    response_0 = requests.get(f"{url}dm/list/v1", params={
        'token': me
    })
    assert response_0.status_code == 200
    result_0 = response_0.json()
    assert type(result_0['dms']) == list
    assert len(result_0['dms']) == 0
    
    # Now make one dm
    girlfriend = three_new_sample_users['sample_uid_1']
    girlfriends_token = three_new_sample_users['sample_token_1']
    girlfriend_hndl = three_new_sample_users['sample_handle_1']
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        'token': me,
        'u_ids': [girlfriend],
    }).json()['dm_id']
    response_1 = requests.get(f"{url}dm/list/v1", params={
        'token': me
    })
    response_2 = requests.get(f"{url}dm/list/v1", params={
        'token': girlfriends_token
    })
    assert response_1.status_code == 200
    assert response_2.status_code == response_1.status_code
    result_1 = response_1.json()
    result_2 = response_2.json()
    assert type(result_1['dms']) == list
    assert len(result_1['dms']) == 1
    assert result_1 == result_2
    assert result_1['dms'] == [{'dm_id': dm_1, 'name': f'{girlfriend_hndl}, {my_hndl}'}]

    # Now make one more dm
    ur_mom = three_new_sample_users['sample_uid_2']
    ur_moms_token = three_new_sample_users['sample_token_2']
    ur_moms_hndl = three_new_sample_users['sample_handle_2']
    dm_2 = requests.post(f"{url}dm/create/v1", json={
        'token': me,
        'u_ids': [ur_mom],
    }).json()['dm_id']
    response_3 = requests.get(f"{url}dm/list/v1", params={
        'token': me
    })
    response_4 = requests.get(f"{url}dm/list/v1", params={
        'token': ur_moms_token
    })
    assert response_3.status_code == 200
    assert response_4.status_code == response_3.status_code
    result_3 = response_3.json()
    result_4 = response_4.json()
    assert type(result_3['dms']) == list
    assert type(result_4['dms']) == list
    assert len(result_3['dms']) == 2
    assert len(result_4['dms']) == 1
    assert result_4['dms'][0] in result_3['dms']
    assert result_4['dms'][0] == {'dm_id': dm_2, 'name': f'{ur_moms_hndl}, {my_hndl}'}

# Tests valid use of dm/list/v1 with the creation of 1 three person dm
def test_with_one_threemember_dm(reset_data_store, three_new_sample_users):
    me = three_new_sample_users['sample_token_0']
    my_hndl = three_new_sample_users['sample_handle_0']
    # No dms exist yet
    response_0 = requests.get(f"{url}dm/list/v1", params={
        'token': me
    })
    assert response_0.status_code == 200
    result_0 = response_0.json()
    assert type(result_0['dms']) == list
    assert len(result_0['dms']) == 0
    
    # Now add yourself and two others to a dm
    girlfriend = three_new_sample_users['sample_uid_1']
    girlfriends_token = three_new_sample_users['sample_token_1']
    girlfriend_hndl = three_new_sample_users['sample_handle_1']
    ur_mom = three_new_sample_users['sample_uid_2']
    ur_moms_token = three_new_sample_users['sample_token_2']
    ur_moms_hndl = three_new_sample_users['sample_handle_2']
    the_dm_id = requests.post(f"{url}dm/create/v1", json={
        'token': me,
        'u_ids': [girlfriend, ur_mom],
    }).json()['dm_id']


    #request the lists
    response_0 = requests.get(f"{url}dm/list/v1", params={
        'token': me
    })
    assert response_0.status_code == 200
    response_1 = requests.get(f"{url}dm/list/v1", params={
        'token': girlfriends_token
    })
    assert response_1.status_code == 200
    response_2 = requests.get(f"{url}dm/list/v1", params={
        'token': ur_moms_token
    })
    assert response_2.status_code == 200
    
    #check the lists
    result_0 = response_0.json()
    result_1 = response_1.json()
    result_2 = response_2.json()
    assert type(result_0['dms']) == list
    assert len(result_0['dms']) == 1
    assert result_0 == result_1
    assert result_1 == result_2
    assert result_0['dms'] == [{'dm_id': the_dm_id, 'name': f'{ur_moms_hndl}, {girlfriend_hndl}, {my_hndl}'}]
