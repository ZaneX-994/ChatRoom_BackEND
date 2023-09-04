import pytest
import requests
from src.config import url
from src.error import InputError
from tests.channel_invite_v2_test import three_new_sample_users

@pytest.fixture
def reset_datastore():
	requests.delete(f"{url}clear/v1")

# Test case for successfully reacting to a message
def test_message_react_v1_successful(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", json={
        'token': three_new_sample_users['sample_token_0'], 
        'name': 'newChannel', 
        'is_public': True,
    }).json()

    message = requests.post(f"{url}message/send/v1", json={
        'token': three_new_sample_users['sample_token_0'],
        'channel_id': new_channel['channel_id'],
        'message': 'I am DEAD!',
    }).json()
                               
    response = requests.post(f"{url}/message/react/v1", json={
        'token': three_new_sample_users['sample_token_0'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == 200

    # Get message reaction.
    react = requests.get(f"{url}channel/messages/v2", params={
        'token': three_new_sample_users['sample_token_0'],
        'channel_id': new_channel['channel_id'],
        'start': 0,
    }).json()['messages'][0]['reacts'][0]

    assert react['react_id'] == 1
    assert react['u_ids'] == [three_new_sample_users['sample_uid_0']]
    assert react['is_this_user_reacted'] == True


# Test case when message_id refers to an invalid message
def test_message_react_v1_invalid_message(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    requests.post(f"{url}message/send/v1", 
                        json={'token': three_new_sample_users['sample_token_0'],
                                'channel_id': new_channel['channel_id'],
                                'message': 'I am DEAD!',}).json()

    message1_react = requests.post(f"{url}/message/react/v1",
                                        json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': 123,
                                            'react_id': 1})

    assert message1_react.status_code == InputError.code

    new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

    requests.post(f"{url}message/senddm/v1", 
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'dm_id': new_dm['dm_id'],
                                    'message': 'I am DEAD!',
                                    }).json()

    message2_react = requests.post(f"{url}/message/react/v1",
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'message_id': 456,
                                        'react_id': 1})

    assert message2_react.status_code == InputError.code

# Test case when react id is invalid
def test_message_react_v1_invalid_react_id(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    message = requests.post(f"{url}message/send/v1", 
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'channel_id': new_channel['channel_id'],
                                        'message': 'I am DEAD!'}).json()

    response = requests.post(f"{url}/message/react/v1",
                                json={'token': three_new_sample_users['sample_token_0'],
                                                'message_id': message['message_id'],
                                                'react_id': 3})

    assert response.status_code == InputError.code

# Test case when the react from the auth user already exists
def test_message_react_v1_react_exists(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    message1 = requests.post(f"{url}message/send/v1", 
                        json={'token': three_new_sample_users['sample_token_0'],
                                'channel_id': new_channel['channel_id'],
                                'message': 'I am DEAD!'}).json()

    requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message1['message_id'],
                                            'react_id': 1})

    message2_react = requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message1['message_id'],
                                            'react_id': 1})

    assert message2_react.status_code == InputError.code

# Test case when the authorised user is not a member of a particular channel
def test_message_react_v1_auth_id_not_member(reset_datastore, three_new_sample_users):
    requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    new_channel2 = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_1'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    message = requests.post(f"{url}message/send/v1", 
                        json={'token': three_new_sample_users['sample_token_1'],
                                'channel_id': new_channel2['channel_id'],
                                'message': 'I am DEAD!'}).json()

    message_react = requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_1'],
                                            'message_id': message['message_id'],
                                            'react_id': 1})

    assert message_react.status_code == 200

    requests.post(f"{url}dm/create/v1",
					json={'token': three_new_sample_users['sample_token_0'],
							'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

    new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_1'],
                                    'u_ids': [three_new_sample_users['sample_uid_2']]}).json()

    message_id2 = requests.post(f"{url}message/senddm/v1", 
                            json={'token': three_new_sample_users['sample_token_1'],
                                    'dm_id': new_dm['dm_id'],
                                    'message': 'I am DEAD!',
                                    }).json()

    message2_react = requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_2'],
                                            'message_id': message_id2['message_id'],
                                            'react_id': 1})

    assert message2_react.status_code == 200
# Test case when a member has not reacted to a message
def test_message_react_v1_auth_id_not_reacted(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    requests.post(f"{url}channel/invite/v2", 
                        json={'token': three_new_sample_users['sample_token_0'], 
                        'channel_id': new_channel['channel_id'],
                        'u_id': three_new_sample_users['sample_uid_1']})
    # new_channel: token 0 and token 1
    message = requests.post(f"{url}message/send/v1", 
                        json={'token': three_new_sample_users['sample_token_0'],
                                'channel_id': new_channel['channel_id'],
                                'message': 'I am DEAD!'}).json()

    requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message['message_id'],
                                            'react_id': 1})

    message_react_again = requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_1'],
                                            'message_id': message['message_id'],
                                            'react_id': 1})

    assert message_react_again.status_code == 200

# Test case when a particular reaction to a message does not exist
def test_message_react_v1_react_non_existent(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    requests.post(f"{url}channel/invite/v2", 
                        json={'token': three_new_sample_users['sample_token_0'], 
                        'channel_id': new_channel['channel_id'],
                        'u_id': three_new_sample_users['sample_uid_1']})

    # new_channel: token 0 and token 1
    message = requests.post(f"{url}message/send/v1", 
                        json={'token': three_new_sample_users['sample_token_0'],
                                'channel_id': new_channel['channel_id'],
                                'message': 'I am DEAD!'}).json()

    requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message['message_id'],
                                            'react_id': 1})

    message_react_again = requests.post(f"{url}/message/react/v1",
                                    json={'token': three_new_sample_users['sample_token_1'],
                                            'message_id': message['message_id'],
                                            'react_id': 2})

    assert message_react_again.status_code == 200 
    
