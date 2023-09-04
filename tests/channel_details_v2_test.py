import pytest
import requests
from src.config import url
from src.error import InputError, AccessError
from tests.channel_invite_v2_test import three_new_sample_users


INVALID_TOKEN = 12345

INVALID_CHNL_ID = 'invalid@98'

CHANNEL_ID_INV = 19023

@pytest.fixture
def reset_datastore():
    requests.delete(f"{url}clear/v1")

# Test case for successfully retrieving the channel details
def test_channel_details_v2_successful(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                'name': 'newChannel', 'is_public': True}).json()
    response = requests.get(f"{url}channel/details/v2",
                            params = {'token': three_new_sample_users['sample_token_0'],
                                    'channel_id': new_channel['channel_id']})
    assert response.status_code == 200

# Test case when passing an invalid token type as a parameter to the function ~ raises AccessError
def test_channel_details_v2_token_invalidtype(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                'name': 'newChannel', 'is_public': True}).json()
    response = requests.get(f"{url}channel/details/v2",
                            params = {'token': INVALID_TOKEN ,
                                    'channel_id': new_channel['channel_id']})
    assert response.status_code == AccessError.code

# Test case for a channel_id not referring to a valid channel ~ raise InputError
def test_channel_details_v2_invalid_channel(reset_datastore, three_new_sample_users):
    response = requests.get(f"{url}channel/details/v2",
                        params = {'token': three_new_sample_users['sample_token_0'] ,
                                'channel_id': CHANNEL_ID_INV })
    
    assert response.status_code == InputError.code

# Test case when the token passed in as the parameter to the function 
# refers to a non-channel-member ~ raises AccessError
def test_channel_details_v2_token_not_member(reset_datastore, three_new_sample_users):
    new_channel = requests.post(f"{url}channels/create/v2", 
                                json={'token': three_new_sample_users['sample_token_0'], 
                                'name': 'newChannel', 'is_public': True}).json()
    response = requests.get(f"{url}channel/details/v2",
                        params = {'token': three_new_sample_users['sample_token_1'] ,
                                'channel_id': new_channel['channel_id'] })
    assert response.status_code == AccessError.code
