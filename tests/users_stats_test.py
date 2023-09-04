import pytest
import requests

from src.config import url
from src.error import InputError, AccessError
from tests.dm_create_test import reset, user0, user1


@pytest.fixture
def user0_channel_id(user0):
    return requests.post(f"{url}channels/create/v2", json={
        'token': user0['token'],
        'name': "General",
        'is_public': True,
    }).json()['channel_id']


@pytest.fixture
def user0_dm_id(user0):
    return requests.post(f"{url}dm/create/v1", json={
        'token': user0['token'],
        'u_ids': [],
    }).json()['dm_id']


def send_channel_message(token, channel_id):
    return requests.post(f"{url}message/send/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': "Hello!",
    }).json()['message_id']


def send_dm_message(token, dm_id):
    return requests.post(f"{url}message/senddm/v1", json={
        'token': token,
        'dm_id': dm_id,
        'message': "Hello!",
    }).json()['message_id']


# Default statistics.
def test_users_stats_empty(reset, user0):
    stats = requests.get(f"{url}users/stats/v1", params={
        'token': user0['token'],
    }).json()['workspace_stats']

    assert stats['channels_exist'][0]['num_channels_exist'] == 0
    assert stats['dms_exist'][0]['num_dms_exist'] == 0
    assert stats['messages_exist'][0]['num_messages_exist'] == 0
    assert stats['utilization_rate'] == 0.0


# Send one channel message.
def test_users_stats_one_user_channel_message(reset, user0, user0_channel_id):
    send_channel_message(user0['token'], user0_channel_id)
    stats = requests.get(f"{url}users/stats/v1", params={
        'token': user0['token'],
    }).json()['workspace_stats']

    assert stats['channels_exist'][0]['num_channels_exist'] == 0
    assert stats['channels_exist'][1]['num_channels_exist'] == 1
    assert stats['messages_exist'][0]['num_messages_exist'] == 0
    assert stats['messages_exist'][1]['num_messages_exist'] == 1
    assert stats['utilization_rate'] == 1.0


# Create and remove a message.
def test_users_stats_removed_message(reset, user0, user0_channel_id):
    message_id = send_channel_message(user0['token'], user0_channel_id)
    requests.delete(f"{url}message/remove/v1", json={
        'token': user0['token'],
        'message_id': message_id,
    })

    stats = requests.get(f"{url}users/stats/v1", params={
        'token': user0['token'],
    }).json()['workspace_stats']

    assert stats['messages_exist'][0]['num_messages_exist'] == 0
    assert stats['messages_exist'][1]['num_messages_exist'] == 1
    assert stats['messages_exist'][2]['num_messages_exist'] == 0
    assert stats['utilization_rate'] == 1.0


# Two users with one in channel.
def test_users_stats_two_users_lone_channel(reset, user0, user0_channel_id, user1):
    stats = requests.get(f"{url}users/stats/v1", params={
        'token': user0['token'],
    }).json()['workspace_stats']

    assert stats['channels_exist'][0]['num_channels_exist'] == 0
    assert stats['channels_exist'][1]['num_channels_exist'] == 1
    assert stats['utilization_rate'] == 0.5


# Two users with one in dm.
def test_users_stats_two_users_lone_dm(reset, user0, user0_dm_id, user1):
    send_dm_message(user0['token'], user0_dm_id)
    stats = requests.get(f"{url}users/stats/v1", params={
        'token': user0['token'],
    }).json()['workspace_stats']

    assert stats['dms_exist'][0]['num_dms_exist'] == 0
    assert stats['dms_exist'][1]['num_dms_exist'] == 1
    assert stats['messages_exist'][0]['num_messages_exist'] == 0
    assert stats['messages_exist'][1]['num_messages_exist'] == 1
    assert stats['utilization_rate'] == 0.5


# Two users with one deleted.
def test_users_stats_deleted_user(reset, user0, user0_dm_id, user1):
    # Remove useless user.
    requests.delete(f"{url}admin/user/remove/v1", json={
        'token': user0['token'],
        'u_id': user1['auth_user_id'],
    })

    stats = requests.get(f"{url}users/stats/v1", params={
        'token': user0['token'],
    }).json()['workspace_stats']
    assert stats['utilization_rate'] == 1.0

