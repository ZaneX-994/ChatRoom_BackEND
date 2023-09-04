import pytest
import requests
from src.config import url
from src.error import InputError
from tests.channel_invite_v2_test import three_new_sample_users

@pytest.fixture
def reset_datastore():
	requests.delete(f"{url}clear/v1")

# Test case for successfully removing a react from a message
def test_message_unreact_v1_successful(reset_datastore, three_new_sample_users):
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

	user0_unreacts = requests.post(f"{url}/message/unreact/v1",
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'message_id': message['message_id'],
                                        'react_id': 1})

	assert user0_unreacts.status_code == 200  

	requests.post(f"{url}/message/react/v1",
                    json={'token': three_new_sample_users['sample_token_0'],
                            'message_id': message['message_id'],
                            'react_id': 1})   

	requests.post(f"{url}/message/react/v1",
                                json={'token': three_new_sample_users['sample_token_1'],
                                        'message_id': message['message_id'],
                                        'react_id': 1})

	user1_unreacts = requests.post(f"{url}/message/unreact/v1",
                                json={'token': three_new_sample_users['sample_token_1'],
                                        'message_id': message['message_id'],
                                        'react_id': 1})

	assert user1_unreacts.status_code == 200  

	requests.post(f"{url}/message/react/v1",
                    json={'token': three_new_sample_users['sample_token_0'],
                            'message_id': message['message_id'],
                            'react_id': 1})

	requests.post(f"{url}/message/react/v1",
                                json={'token': three_new_sample_users['sample_token_1'],
                                        'message_id': message['message_id'],
                                        'react_id': 2})

	user1_unreacts = requests.post(f"{url}/message/unreact/v1",
                                json={'token': three_new_sample_users['sample_token_1'],
                                        'message_id': message['message_id'],
                                        'react_id': 2})

	assert user1_unreacts.status_code == 200
        



	new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

	message2 = requests.post(f"{url}message/senddm/v1", 
							json={'token': three_new_sample_users['sample_token_0'],
									'dm_id': new_dm['dm_id'],
									'message': 'I am DEAD!',
									}).json()

	requests.post(f"{url}message/react/v1",
					json={'token': three_new_sample_users['sample_token_0'],
							'message_id': message2['message_id'],
							'react_id': 2})

	user0_unreacts = requests.post(f"{url}/message/unreact/v1",
								json={'token': three_new_sample_users['sample_token_0'],
									'message_id':  message2['message_id'],
									'react_id': 2})
	
	assert user0_unreacts.status_code == 200

	requests.post(f"{url}dm/create/v1",
					json={'token': three_new_sample_users['sample_token_0'],
							'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

	new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_1'],
                                    'u_ids': [three_new_sample_users['sample_uid_2']]}).json()

	message2 = requests.post(f"{url}message/senddm/v1", 
							json={'token': three_new_sample_users['sample_token_1'],
									'dm_id': new_dm['dm_id'],
									'message': 'I am DEAD!',
									}).json()

	requests.post(f"{url}message/react/v1",
					json={'token': three_new_sample_users['sample_token_0'],
							'message_id': message2['message_id'],
							'react_id': 2})

	user1_unreacts = requests.post(f"{url}/message/unreact/v1",
								json={'token': three_new_sample_users['sample_token_1'],
									'message_id':  message2['message_id'],
									'react_id': 2})

	assert user1_unreacts.status_code == 200
	
# Test case when message_id refers to an invalid message
def test_message_unreact_v1_invalid_message(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    message = requests.post(f"{url}message/send/v1", 
                        json={'token': three_new_sample_users['sample_token_0'],
                                'channel_id': new_channel['channel_id'],
                                'message': 'I am DEAD!'}).json()

    requests.post(f"{url}/message/react/v1",
                    json={'token': three_new_sample_users['sample_token_0'],
                            'message_id': message['message_id'],
                            'react_id': 1})
            
    user0_unreacts = requests.post(f"{url}/message/unreact/v1",
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'message_id': 123,
                                        'react_id': 1})

    assert user0_unreacts.status_code == InputError.code

    new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

    message2 = requests.post(f"{url}message/senddm/v1", 
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'dm_id': new_dm['dm_id'],
                                    'message': 'I am DEAD!',
                                    }).json()

    requests.post(f"{url}message/react/v1",
                    json={'token': three_new_sample_users['sample_token_0'],
                            'message_id': message2['message_id'],
                            'react_id': 2})
                
    user0_unreacts_again = requests.post(f"{url}/message/unreact/v1",
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'message_id':  456,
                                        'react_id': 2})
                            
    assert user0_unreacts_again.status_code == InputError.code

# Test case when react id is invalid
def test_message_unreact_v1_invalid_react_id(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    message = requests.post(f"{url}message/send/v1", 
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'channel_id': new_channel['channel_id'],
                                        'message': 'I am DEAD!'}).json()

    requests.post(f"{url}/message/react/v1",
                    json={'token': three_new_sample_users['sample_token_0'],
                                    'message_id': message['message_id'],
                                    'react_id': 1})

    user_unreacts = requests.post(f"{url}/message/unreact/v1",
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'message_id': message['message_id'],
                                        'react_id': 3})

    assert user_unreacts.status_code == InputError.code

# Test case when the react from the auth user already exists
def test_message_unreact_v1_react_not_exists(reset_datastore, three_new_sample_users):
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

    requests.post(f"{url}/message/react/v1",
                    json={'token': three_new_sample_users['sample_token_1'],
                            'message_id': message1['message_id'],
                            'react_id': 2})

    user1_unreacts = requests.post(f"{url}/message/unreact/v1",
                                json={'token': three_new_sample_users['sample_token_1'],
                                        'message_id': message1['message_id'],
                                        'react_id': 1})
                                        
    assert user1_unreacts.status_code == InputError.code
