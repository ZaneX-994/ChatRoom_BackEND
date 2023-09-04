import pytest
from src.config import url
import requests
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from tests.dm_create_test import user0, user1, user2
import time
from tests.message_edit_v1_test import check_message_dm

@pytest.fixture
def clear():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def dm_id(user0, user1):
    """
    Constructs a DM and returns its dm_id with user0.
    """
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [user1['auth_user_id']],
    }).json()
    return result['dm_id']

@pytest.fixture
def time_sent(clear):
    """
    Create the time to sendlater
    """
    time_sent = time.time()
    return time_sent + 1

def test_bad_parameters(clear, dm_id, time_sent):
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': 1,
        'dm_id': dm_id,
        'message': '1',
        'time_sent': time_sent,
    })
    assert response.status_code == AccessError.code

def test_invalid_dm_id(clear, user0, time_sent):
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': user0['token'],
        'dm_id': '3',
        'message': '1',
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code

def test_invalid_length_long_dm(clear, user0, dm_id, time_sent):
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': 'hi' * 1000,
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': '',
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code

def test_invalid_time_senddm(clear, user0, dm_id):
    time_now = time.time()
    invalid_time = time_now - 1
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': 'hi',
        'time_sent': invalid_time,
    })
    assert response.status_code == InputError.code

def test_user_not_dm_members(clear, user0, user2, dm_id, time_sent):
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': user2['token'],
        'dm_id': dm_id,
        'message': 'hi',
        'time_sent': time_sent,
    })
    assert response.status_code == AccessError.code

def test_sendlaterdm_message(clear, user0, dm_id, time_sent):
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': 'hi',
        'time_sent': time_sent,
    })
    assert response.status_code == 200
    # Wait 1 second for check the messsage after sendlater
    time.sleep(1)
    message = check_message_dm(user0, dm_id)
    assert message[0]['message'] == 'hi'

# Check message at unsuitable time
def test_invalid_sendlaterdm_message(clear, user0, dm_id, time_sent):
    response = requests.post(f"{url}message/sendlaterdm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': 'hi',
        'time_sent': time_sent,
    })
    assert response.status_code == 200
    message = check_message_dm(user0, dm_id)
    assert len(message) == 0