import pytest
import requests
from src.config import url
from src.error import InputError, AccessError
from tests.channel_invite_v2_test import three_new_sample_users

@pytest.fixture
def reset_datastore():
	requests.delete(f"{url}clear/v1")

# Test case for successfully adding a pin to a message
def test_message_pin_v1_successful(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    message_id = requests.post(f"{url}message/send/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'channel_id': new_channel['channel_id'],
                                    'message': 'I am DEAD!'}).json()

    response1 = requests.post(f"{url}message/pin/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message_id['message_id']})

    response2 = requests.get(f"{url}channel/messages/v2", 
                            params={'token':  three_new_sample_users['sample_token_0'],
                                    'channel_id': new_channel['channel_id'],
                                    'start': 0}).json()

    assert response2['messages'][0]['is_pinned'] == True 
    assert response1.status_code == 200

    new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

    message_id2 = requests.post(f"{url}message/senddm/v1", 
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'dm_id': new_dm['dm_id'],
                                    'message': 'I am DEAD!',
                                    }).json()

    response3 = requests.post(f"{url}message/pin/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message_id2['message_id']})

    response4 = requests.get(f"{url}dm/messages/v1", 
                            params={'token':  three_new_sample_users['sample_token_0'],
                                    'dm_id': new_dm['dm_id'],
                                    'start': 0}).json()

    assert response4['messages'][0]['is_pinned'] == True
    assert response3.status_code == 200
# Test case when message_id refers to an invalid message
def test_message_pin_v1_invalid_message(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    requests.post(f"{url}message/send/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'channel_id': new_channel['channel_id'],
                                    'message': 'I am DEAD!'}).json()

    response1 = requests.post(f"{url}message/pin/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': 123})

    assert response1.status_code == InputError.code

    new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

    requests.post(f"{url}message/senddm/v1", 
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'dm_id': new_dm['dm_id'],
                                    'message': 'I am DEAD!',
                                    }).json()

    response2 = requests.post(f"{url}message/pin/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': 456})   

    assert response2.status_code == InputError.code                    
# Test case when the message is already pinned
def test_message_pin_v1_already_pinned(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    message_id = requests.post(f"{url}message/send/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'channel_id': new_channel['channel_id'],
                                    'message': 'I am DEAD!'}).json()

    requests.post(f"{url}message/pin/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message_id['message_id']})

    response1 = requests.post(f"{url}message/pin/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message_id['message_id']})

    assert response1.status_code == InputError.code

    new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

    message_id2 = requests.post(f"{url}message/senddm/v1", 
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'dm_id': new_dm['dm_id'],
                                    'message': 'I am DEAD!',
                                    }).json()

    requests.post(f"{url}message/pin/v1",
                    json={'token': three_new_sample_users['sample_token_0'],
                            'message_id': message_id2['message_id']})

    response2 = requests.post(f"{url}message/pin/v1",
                                    json={'token': three_new_sample_users['sample_token_0'],
                                            'message_id': message_id2['message_id']})  

    assert response2.status_code == InputError.code     
# Test case when autharised user does not have owner permissions
def test_message_pin_v1_auth_not_owner(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                        'name': 'newChannel', 
                                        'is_public': True}).json()

    requests.post(f"{url}channel/invite/v2", 
                    json={'token': three_new_sample_users['sample_token_0'], 
                    'channel_id': new_channel['channel_id'],
                    'u_id': three_new_sample_users['sample_uid_1']})

    message_id = requests.post(f"{url}message/send/v1",
                                json={'token': three_new_sample_users['sample_token_0'],
                                        'channel_id': new_channel['channel_id'],
                                        'message': 'I am DEAD!'}).json()

    response = requests.post(f"{url}message/pin/v1",
                            json={'token': three_new_sample_users['sample_token_1'],
                                    'message_id': message_id['message_id']})

    assert response.status_code == AccessError.code

    new_dm = requests.post(f"{url}dm/create/v1",
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

    message_id2 = requests.post(f"{url}message/senddm/v1", 
                            json={'token': three_new_sample_users['sample_token_0'],
                                    'dm_id': new_dm['dm_id'],
                                    'message': 'I am DEAD!',
                                    }).json()

    response2 = requests.post(f"{url}message/pin/v1",
                    json={'token': three_new_sample_users['sample_token_1'],
                            'message_id': message_id2['message_id']})

    assert response2.status_code == AccessError.code

# Test case when the authorised user is not a member of a particular channel
def test_message_pin_v1_auth_id_not_member(reset_datastore, three_new_sample_users):
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

	message_pin = requests.post(f"{url}message/pin/v1",
                            json={'token': three_new_sample_users['sample_token_1'],
                                    'message_id': message['message_id']})

	assert message_pin.status_code == 200

	requests.post(f"{url}dm/create/v1",
							json={'token': three_new_sample_users['sample_token_0'],
									'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

	new_dm = requests.post(f"{url}dm/create/v1",
							json={'token': three_new_sample_users['sample_token_2'],
									'u_ids': [three_new_sample_users['sample_uid_1']]}).json()

	message_id2 = requests.post(f"{url}message/senddm/v1", 
							json={'token': three_new_sample_users['sample_token_2'],
									'dm_id': new_dm['dm_id'],
									'message': 'I am DEAD!',
									}).json()

	response3 = requests.post(f"{url}message/pin/v1",
									json={'token': three_new_sample_users['sample_token_2'],
											'message_id': message_id2['message_id']})
											
	assert response3.status_code == 200
