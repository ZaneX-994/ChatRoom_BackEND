import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
from tests.dm_create_test import reset, user0, user1

SAMPLE_MESSAGE = "Hello!"


@pytest.fixture
def dm_id(user0):
    """
    Constructs a DM and returns its dm_id with user0.
    """
    result = requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [],
    }).json()
    return result['dm_id']


def test_dm_messages_1(reset, dm_id, user0):
    message_id = send_sample_message(dm_id, user0)
    result = requests.get(f"{url}dm/messages/v1", params={
        'token': user0['token'],
        'dm_id': dm_id,
        'start': 0,
    }).json()

    assert len(result['messages']) == 1
    assert result['start'] == 0
    assert result['end'] == -1

    message = result['messages'][0]
    assert message['message_id'] == message_id
    assert message['u_id'] == user0['auth_user_id']
    assert message['message'] == SAMPLE_MESSAGE
    assert 'time_sent' in message


def test_dm_messages_50(reset, dm_id, user0):
    for _i in range(50):
        send_sample_message(dm_id, user0)

    result = requests.get(f"{url}dm/messages/v1", params={
        'token': user0['token'],
        'dm_id': dm_id,
        'start': 0,
    }).json()

    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == -1


# Test pagination with 50 messages per page.
def test_dm_messages_51(reset, dm_id, user0):
    for _i in range(51):
        send_sample_message(dm_id, user0)

    result = requests.get(f"{url}dm/messages/v1", params={
        'token': user0['token'],
        'dm_id': dm_id,
        'start': 0,
    }).json()

    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == 50


# Not enough messages.
def test_dm_messages_start_out_of_bounds(reset, dm_id, user0):
    result = requests.get(f"{url}dm/messages/v1", params={
        'token': user0['token'],
        'dm_id': dm_id,
        'start': 1,
    })
    assert result.status_code == InputError.code


# DM with id 0 does not exist.
def test_dm_messages_dm_id_invalid(reset, user0):
    result = requests.get(f"{url}dm/messages/v1", params={
        'token': user0['token'],
        'dm_id': 0,
        'start': 0,
    })
    assert result.status_code == InputError.code


# Outside user is not present in DM.
def test_dm_messages_unauthorized(reset, dm_id, user1):
    result = requests.get(f"{url}dm/messages/v1", params={
        'token': user1['token'],
        'dm_id': dm_id,
        'start': 0,
    })
    assert result.status_code == AccessError.code


def send_sample_message(dm_id, user):
    """
    Sends a sample message and returns its id.
    """
    result = requests.post(f"{url}message/senddm/v1", json={
        'token': user['token'],
        'dm_id': dm_id,
        'message': SAMPLE_MESSAGE,
    }).json()
    return result['message_id']

