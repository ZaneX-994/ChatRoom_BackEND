import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
from tests.dm_create_test import reset, user0, user1


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


def test_senddm_successful(reset, dm_id, user0):
    result = requests.post(f"{url}message/senddm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': "Hello!",
    }).json()
    assert 'message_id' in result


def test_senddm_length_too_small(reset, dm_id, user0):
    result = requests.post(f"{url}message/senddm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': "",
    })
    assert result.status_code == InputError.code


def test_senddm_length_too_long(reset, dm_id, user0):
    result = requests.post(f"{url}message/senddm/v1", json={
        'token': user0['token'],
        'dm_id': dm_id,
        'message': "a" * 1001,
    })
    assert result.status_code == InputError.code


# DM with id 0 does not exist.
def test_senddm_dm_id_invalid(reset, user0):
    result = requests.post(f"{url}message/senddm/v1", json={
        'token': user0['token'],
        'dm_id': 0,
        'message': "Bad!",
    })
    assert result.status_code == InputError.code


# Outside user is not present in DM.
def test_senddm_unauthorized(reset, dm_id, user1):
    result = requests.post(f"{url}message/senddm/v1", json={
        'token': user1['token'],
        'dm_id': dm_id,
        'message': "Intrusion!",
    })
    assert result.status_code == AccessError.code

