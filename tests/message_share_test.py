from email import message
import pytest
import requests
from src.config import url
from src.error import InputError, AccessError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, auth_register

VALID_NAME = 'channelOne'
VALID_MASSAGE = 'valid message'
INVALID_MASSAGE = str('a' * 1001)

@pytest.fixture
def reset():
	requests.delete(f"{url}clear/v1")

@pytest.fixture
def sample_users():
    userOne = auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

    userTWo = auth_register("a" + VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

    userThree = auth_register("b" + VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

    return {
        'userOne': userOne,
        'userTwo': userTWo,
        'userThree': userThree
    }


@pytest.fixture
def sample_channels(sample_users):
    channelOne = requests.post(f'{url}channels/create/v2', json={
        'token': sample_users['userOne']['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    channelTwo = requests.post(f'{url}channels/create/v2', json={
        'token': sample_users['userTwo']['token'],
        'name': VALID_NAME,
        'is_public': True,
    }).json()

    return {
        'channelOne': channelOne,
        'channelTwo': channelTwo,
    }

@pytest.fixture

def sample_dms(sample_users):

    dm_One = requests.post(f'{url}dm/create/v1', json={
        'token': sample_users['userOne']['token'],
        'u_ids': [sample_users['userTwo']['auth_user_id']],
    }).json()

    dm_Two = requests.post(f'{url}dm/create/v1', json={
        'token': sample_users['userTwo']['token'],
        'u_ids': [sample_users['userThree']['auth_user_id']],
    }).json()

    return {
        'dm_One': dm_One,
        'dm_Two': dm_Two,
    }

# test invalid og_message_id
def test_invalid_og_message_id(reset, sample_users, sample_channels):

    # share message from channelOne to channelTwo with non-exist og_message_id
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': 1,
        'message': '',
        'channel_id': sample_channels['channelTwo']['channel_id'],
        'dm_id': -1,
    })

    assert share_result.status_code == InputError.code

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # userOne share message from channelOne to channelTwo 
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'] + 1,
        'message': '',
        'channel_id': sample_channels['channelTwo']['channel_id'],
        'dm_id': -1,
    })

    assert share_result.status_code == InputError.code

# test invalid token
def test_invalid_token(reset, sample_users, sample_channels): 

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # share message from channelOne to channelTwo with invalid token
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'] + '1',
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': sample_channels['channelTwo']['channel_id'],
        'dm_id': -1,
    })

    assert share_result.status_code == AccessError.code

# test invalid message length
def test_invalid_message_length(reset, sample_users, sample_channels):

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # share message from channelOne to channelTwo with overlong additional message
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': INVALID_MASSAGE,
        'channel_id': sample_channels['channelTwo']['channel_id'],
        'dm_id': -1,
    })

    assert share_result.status_code == InputError.code

# test invalid channel_id (doesn's exist)
def test_non_exist_channel_id(reset, sample_users, sample_channels):

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # share message from channelOne to another channel with invalid channel_id
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': sample_channels['channelTwo']['channel_id'] + sample_channels['channelOne']['channel_id'] + 1,
        'dm_id': -1,
    })    

    assert share_result.status_code == InputError.code

# test invalid dm_id (doesn't exist)
def test_non_exist_dm_id(reset, sample_users, sample_dms, sample_channels):

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # share message from channelOne to a dm with invalid dm_id
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': sample_dms['dm_Two']['dm_id'] + sample_dms['dm_One']['dm_id'] + 1,
    })    

    assert share_result.status_code == InputError.code

# both dm_id and channel_id are invalid
def test_both_channel_id_and_dm_id_invalid(reset, sample_users, sample_dms, sample_channels):

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': '1',
        'dm_id': '1',
    })

    assert share_result.status_code == InputError.code

    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': sample_channels['channelOne']['channel_id'],
        'dm_id': sample_dms['dm_One']['dm_id'],
    })

    assert share_result.status_code == InputError.code

# test share message to channel/dm that is not joined
def test_share_message_to_not_joined_channel_or_dm(reset, sample_users, sample_dms, sample_channels):

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # userOne share message from channelOne to dm_Two
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': sample_dms['dm_Two']['dm_id'],
    })

    assert share_result.status_code == AccessError.code

    # userOne share message from channelOne to channelTwo
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': sample_channels['channelTwo']['channel_id'],
        'dm_id': -1,
    })
    
    assert share_result.status_code == AccessError.code
# test share message from channel/dm that is not joined
def test_share_message_from_not_joined_channel_or_dm(reset, sample_users, sample_channels, sample_dms):

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # userTwo share message from channelOne to dm_two
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userTwo']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': sample_dms['dm_Two']['dm_id'],
    })

    assert share_result.status_code == InputError.code

    message_send = requests.post(f'{url}/message/senddm/v1', json={
        'token': sample_users['userOne']['token'],
        'dm_id': sample_dms['dm_One']['dm_id'],
        'message': VALID_MASSAGE,
    }).json()

    # user Three share messge from dm_One to dm_two
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userThree']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': sample_dms['dm_Two']['dm_id'],
    })

    assert share_result.status_code == InputError.code
# test successful share to channel/dm
def test_successful(reset, sample_users, sample_channels, sample_dms):

    message_send = requests.post(f'{url}message/send/v1', json={
        'token': sample_users['userOne']['token'],
        'channel_id': sample_channels['channelOne']['channel_id'],
        'message': VALID_MASSAGE,
    }).json()

    # userOne share message from channelOne to dm_One
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': sample_dms['dm_One']['dm_id'],
    })

    assert 'shared_message_id' in share_result.json()
    assert share_result.status_code == 200


    requests.post(f"{url}channel/invite/v2", json={
        'token': sample_users['userTwo']['token'],
        'channel_id': sample_channels['channelTwo']['channel_id'],
        'u_id': sample_users['userOne']['auth_user_id'],
    })
    # userOne share message from channelOne to channelTwo
    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': sample_channels['channelTwo']['channel_id'],
        'dm_id': -1,
    })

    assert 'shared_message_id' in share_result.json()
    assert share_result.status_code == 200

    # userOne share messages from dm_One to channelOne
    message_send = requests.post(f'{url}/message/senddm/v1', json={
        'token': sample_users['userOne']['token'],
        'dm_id': sample_dms['dm_One']['dm_id'],
        'message': VALID_MASSAGE,
    }).json()

    share_result = requests.post(f'{url}message/share/v1', json={
        'token': sample_users['userOne']['token'],
        'og_message_id': message_send['message_id'],
        'message': '',
        'channel_id': sample_channels['channelOne']['channel_id'],
        'dm_id': -1,
    })

    assert 'shared_message_id' in share_result.json()
    assert share_result.status_code == 200