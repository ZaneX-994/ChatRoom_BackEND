import pytest
import requests
from src.config import url
from src.error import AccessError


@pytest.fixture
def reset_data_store():
    requests.delete(f"{url}clear/v1")


@pytest.fixture
def two_new_sample_users():
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
    response_0 = requests.post(f"{url}auth/register/v2", json=u_0_info)
    response_1 = requests.post(f"{url}auth/register/v2", json=u_1_info)
    assert response_0.status_code == 200
    assert response_1.status_code == 200
    new_usr_0 = response_0.json()
    new_usr_1 = response_1.json()
    assert 'token' in new_usr_0
    assert 'token' in new_usr_1
    assert 'auth_user_id' in new_usr_0
    assert 'auth_user_id' in new_usr_1
    assert type(new_usr_0['token']) == str
    assert type(new_usr_1['token']) == str
    assert type(new_usr_0['auth_user_id']) == int
    assert type(new_usr_1['auth_user_id']) == int
    # there are 2 valid users in the data_store now^
    sample_usrs = {
        'sample_token_0': new_usr_0['token'],
        'sample_uid_0': new_usr_0['auth_user_id'],
        'sample_token_1': new_usr_1['token'],
        'sample_uid_1': new_usr_1['auth_user_id'],
    }
    return sample_usrs

# Tests whether a token parameter unknown to the server makes
# /channels/listall/v2 return an AccessError
def test_unregistered_token(reset_data_store):
    response = requests.get(
        f"{url}channels/listall/v2", params={'token': 'poopyhead'})
    assert response.status_code == AccessError.code

# Tests whether a token of an non-str type makes
# /channels/listall/v2 return an AccessError
def test_invalid_token_types(reset_data_store):
    response = requests.get(
        f"{url}channels/listall/v2", params={'token': -545.2})
    assert response.status_code == AccessError.code
    response = requests.get(
        f"{url}channels/listall/v2", params={'token': 456.66})
    assert response.status_code == AccessError.code
    response = requests.get(
        f"{url}channels/listall/v2", params={'token': False})
    assert response.status_code == AccessError.code
    response = requests.get(
        f"{url}channels/listall/v2", params={'token': True})
    assert response.status_code == AccessError.code

# Tests whether channels/listall/v2 returns an 
# empty list if no channels have been created
def test_with_empty_channels(reset_data_store, two_new_sample_users):
    valid_token_0 = two_new_sample_users['sample_token_0']
    valid_token_1 = two_new_sample_users['sample_token_1']

    # No channels exist yet, so the channels list of dictionaries should be empty
    response_0 = requests.get(
        f"{url}channels/listall/v2", params={'token': valid_token_0})
    response_1 = requests.get(
        f"{url}channels/listall/v2", params={'token': valid_token_1})
    assert response_0.status_code == 200
    assert response_1.status_code == response_0.status_code
    assert response_0.json() == {'channels': []}
    assert response_1.json() == {'channels': []}

# Tests valid use of channels/listall/v2 with the creation of two new channels
def test_with_one_and_two_channels(reset_data_store, two_new_sample_users):
    valid_token_0 = two_new_sample_users['sample_token_0']
    valid_token_1 = two_new_sample_users['sample_token_1']

    # No channels exist yet
    response_0 = requests.get(
        f"{url}channels/listall/v2", params={'token': valid_token_0})
    assert response_0.status_code == 200
    result_0 = response_0.json()
    assert type(result_0['channels']) == list
    assert len(result_0['channels']) == 0

    # Now make one channel
    requests.post(f"{url}channels/create/v2",
                  json={'token': valid_token_0, 'name': 'School', 'is_public': True})
    result_1 = requests.get(
        f"{url}channels/listall/v2", params={'token': valid_token_0}).json()
    # 'channels' list should have 1 c_id/name dict.
    assert type(result_1['channels']) == list
    assert len(result_1['channels']) == 1
    assert type(result_1['channels'][0]['channel_id']) == int
    assert result_1['channels'][0]['name'] == 'School'

    # Make second channel
    requests.post(f"{url}channels/create/v2",
                  json={'token': valid_token_1, 'name': 'Family', 'is_public': False})
    result_2 = requests.get(
        f"{url}channels/listall/v2", params={'token': valid_token_1}).json()
    # 'channels' list should have 2 c_id/name dicts.
    assert type(result_2['channels']) == list
    assert len(result_2['channels']) == 2
    assert type(result_2['channels'][0]['channel_id']) == int
    assert type(result_2['channels'][1]['channel_id']) == int
    assert result_2['channels'][0]['name'] == 'School'
    assert result_2['channels'][1]['name'] == 'Family'
