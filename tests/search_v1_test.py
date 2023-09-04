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
def new_channel(three_new_sample_users):
    token = three_new_sample_users['sample_token_0']
    ch_id = requests.post(f"{url}channels/create/v2", json={
        'token': token, 'name': 'New Channel', 'is_public': True
    }).json()['channel_id']
    return {
        'creator_token': token,
        'ch_id': ch_id,
    }

@pytest.fixture
def new_dm(three_new_sample_users):
    token = three_new_sample_users['sample_token_0']
    dm_id = requests.post(f"{url}dm/create/v1", json={
        'token': token, 'u_ids': [three_new_sample_users['sample_uid_1']],
    }).json()['dm_id']
    return {
        'creator_token': token,
        'dm_id': dm_id,
    }

@pytest.fixture
def send_5_ch_msgs(three_new_sample_users, new_channel):
    # have a new user join the channel
    requests.post(f"{url}channel/join/v2", json={
        'token': three_new_sample_users['sample_token_1'], 'channel_id': new_channel['ch_id'],
    })

    # Create some messages in the channel
    requests.post(f"{url}message/send/v1", json={
        'token': new_channel['creator_token'],
        'channel_id': new_channel['ch_id'],
        'message': 'Hey there Friend A!',
    })
    requests.post(f"{url}message/send/v1", json={
        'token': three_new_sample_users['sample_token_1'],
        'channel_id': new_channel['ch_id'],
        'message': 'Hey, it\'s been a while, do you want to go get french fries sometime and catch up?',
    })
    requests.post(f"{url}message/send/v1", json={
        'token': new_channel['creator_token'],
        'channel_id': new_channel['ch_id'],
        'message': 'Sure',
    })
    requests.post(f"{url}message/send/v1", json={
        'token': three_new_sample_users['sample_token_1'],
        'channel_id': new_channel['ch_id'],
        'message': 'Great, what time is good for you? I\'m free anytime this week.',
    })
    requests.post(f"{url}message/send/v1", json={
        'token': new_channel['creator_token'],
        'channel_id': new_channel['ch_id'],
        'message': 'How about this Friday?',
    })
    requests.post(f"{url}message/send/v1", json={
        'token': three_new_sample_users['sample_token_1'],
        'channel_id': new_channel['ch_id'],
        'message': 'Sounds good. See you then!',
    })

@pytest.fixture
def send_5_dm_msgs(three_new_sample_users, new_dm):
    # Send some messages in the dm
    requests.post(f"{url}message/senddm/v1", json={
        'token': new_dm['creator_token'],
        'dm_id': new_dm['dm_id'],
        'message': 'Hey there Friend B!',
    })
    requests.post(f"{url}message/senddm/v1", json={
        'token': three_new_sample_users['sample_token_1'],
        'dm_id': new_dm['dm_id'],
        'message': 'Hey, it\'s been a while, do you want to go get french fries sometime and catch up?',
    })
    requests.post(f"{url}message/senddm/v1", json={
        'token': new_dm['creator_token'],
        'dm_id': new_dm['dm_id'],
        'message': 'Sure',
    })
    requests.post(f"{url}message/senddm/v1", json={
        'token': three_new_sample_users['sample_token_1'],
        'dm_id': new_dm['dm_id'],
        'message': 'Great, what time is good for you? I\'m free anytime this week.',
    })
    requests.post(f"{url}message/senddm/v1", json={
        'token': new_dm['creator_token'],
        'dm_id': new_dm['dm_id'],
        'message': 'How about this Friday?',
    })
    requests.post(f"{url}message/senddm/v1", json={
        'token': three_new_sample_users['sample_token_1'],
        'dm_id': new_dm['dm_id'],
        'message': 'Sounds good. See you then!',
    })


# Tests valid use of search/v1 with two channel users
def test_search_in_a_channel(reset_data_store, three_new_sample_users, new_channel, send_5_ch_msgs):
    response_0 = requests.get(f"{url}search/v1", params={
        'token': new_channel['creator_token'],
        'query_str': 'fri',
    })
    response_1 = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_1'],
        'query_str': 'Fri',
    })
    # print(f'GIDIT<>><><><><><{response_0.json()}')
    # print(f'GIDIT<>><><><><><{response_1.json()}')
    assert response_0.status_code == 200
    assert response_1.status_code == response_0.status_code
    # print(response_0.json())
    assert 'messages' in response_0.json()
    assert response_1.json() == response_0.json()
    search_results = response_0.json()['messages']
    assert len(search_results) == 3
    for msg in search_results:
        assert 'message_id' in msg
        assert 'u_id' in msg
        assert 'message' in msg
        assert 'time_sent' in msg
        # assert 'reacts' in msg # New in ITER3
        # assert 'is_pinned' in msg # New in ITER3
    assert search_results[0]['message'] == 'Hey there Friend A!'
    assert search_results[1]['message'] == 'Hey, it\'s been a while, do you want to go get french fries sometime and catch up?'
    assert search_results[2]['message'] == 'How about this Friday?'

# Tests valid use of search/v1 with two dm users
def test_search_in_a_dm(reset_data_store, three_new_sample_users, new_dm, send_5_dm_msgs):
    response_0 = requests.get(f"{url}search/v1", params={
        'token': new_dm['creator_token'],
        'query_str': 'fri',
    })
    response_1 = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_1'],
        'query_str': 'Fri',
    })
    assert response_0.status_code == 200
    assert response_1.status_code == response_0.status_code
    assert 'messages' in response_0.json()
    assert response_1.json() == response_0.json()
    search_results = response_0.json()['messages']
    assert len(search_results) == 3
    for msg in search_results:
        assert 'message_id' in msg
        assert 'u_id' in msg
        assert 'message' in msg
        assert 'time_sent' in msg
        # assert 'reacts' in msg # New in ITER3
        # assert 'is_pinned' in msg # New in ITER3
    assert search_results[0]['message'] == 'Hey there Friend B!'
    assert search_results[1]['message'] == 'Hey, it\'s been a while, do you want to go get french fries sometime and catch up?'
    assert search_results[2]['message'] == 'How about this Friday?'

# Tests that for a user that isn't part of any channels/dms,
# search_v1 returns an empty 'messages' list
def test_not_part_of_any_channel_or_dm(reset_data_store, three_new_sample_users, new_channel, new_dm, send_5_ch_msgs, send_5_dm_msgs):
    response = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_2'],
        'query_str': 'random query',
    })
    assert response.status_code == 200
    assert response.json() == {'messages': []}

# Tests that an query string less than 1 character returns InputError
def test_empty_query_str(reset_data_store, three_new_sample_users):
    response = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_0'],
        'query_str': '',
    })
    assert response.status_code == InputError.code

# Tests that an query string more than 1000 characters returns InputError
def test_query_str_too_big(reset_data_store, three_new_sample_users):
    response = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_0'],
        'query_str': 'hello!!'*143,
    })
    assert response.status_code == InputError.code

# Tests whether a token parameter unknown to the server makes
# search/v1 return an AccessError
def test_unregistered_token(reset_data_store, three_new_sample_users):
    response = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_0'] + 'ds32s',
        'query_str': 'hello!',
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_1'] + '435m',
        'query_str': 'hello!',
    })
    assert response.status_code == AccessError.code
    response = requests.get(f"{url}search/v1", params={
        'token': three_new_sample_users['sample_token_2'] + '32*',
        'query_str': 'hello!',
    })
    assert response.status_code == AccessError.code
