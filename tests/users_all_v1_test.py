import json
import pytest
import requests
from src.config import url
from src.error import AccessError

@pytest.fixture
def reset_data_store():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def new_sample_users():
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
    user0 = {
        'u_id': new_usr_0['auth_user_id'],
        'email': u_0_info['email'],
        'name_first': u_0_info['name_first'],
        'name_last': u_0_info['name_last'],
        'handle_str': u_0_info['name_first'].lower() + u_0_info['name_last'].lower(),
    }
    user1 = {
        'u_id': new_usr_1['auth_user_id'],
        'email': u_1_info['email'],
        'name_first': u_1_info['name_first'],
        'name_last': u_1_info['name_last'],
        'handle_str': u_1_info['name_first'].lower() + u_1_info['name_last'].lower(),
    }
    user2 = {
        'u_id': new_usr_2['auth_user_id'],
        'email': u_2_info['email'],
        'name_first': u_2_info['name_first'],
        'name_last': u_2_info['name_last'],
        'handle_str': u_2_info['name_first'].lower() + u_2_info['name_last'].lower(),
    }
    sample_usrs = {
        'u_0': user0,
        'u_1': user1,
        'u_2': user2,
        'token0': new_usr_0['token'],
        'token1': new_usr_1['token'],
        'token2': new_usr_2['token'],
    }
    return sample_usrs

# Tests whether a token parameter unknown to the server makes
# users/all/v1 return an AccessError
def test_unregistered_token(reset_data_store, new_sample_users):
    response = requests.get(f"{url}users/all/v1", params={
        'token': new_sample_users['token0'] + 'Ndf'
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}users/all/v1", params={
        'token': new_sample_users['token1'] + '435m'
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}users/all/v1", params={
        'token': new_sample_users['token2'] + '32*'
    })
    assert response.status_code == AccessError.code

# Tests valid use of users/all/v1 with three users
def test_with_three_users(reset_data_store, new_sample_users):
    response = requests.get(f"{url}users/all/v1", params={
        'token': new_sample_users['token0']
    })
    assert response.status_code == 200
    list_0 = response.json()['users']
    response = requests.get(f"{url}users/all/v1", params={
        'token': new_sample_users['token1']
    })
    assert response.status_code == 200
    list_1 = response.json()['users']
    response = requests.get(f"{url}users/all/v1", params={
        'token': new_sample_users['token2']
    })
    assert response.status_code == 200
    list_2 = response.json()['users']
    assert list_0 == list_1
    assert list_1 == list_2
    sorted_list = [{},{},{}]
    for user in list_1:
        print(int(user['u_id']))
        sorted_list[int(user['u_id'])] = list_1[int(user['u_id'])]
    assert sorted_list == [new_sample_users['u_0'], new_sample_users['u_1'], new_sample_users['u_2']]

