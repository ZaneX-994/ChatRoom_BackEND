import pytest
import requests
from src.auth import PERMISSIONS_MEMBER, PERMISSIONS_OWNER
from src.config import url
from src.error import InputError, AccessError
from tests.channel_invite_v2_test import three_new_sample_users

@pytest.fixture
def reset_datastore():
    requests.delete(f"{url}clear/v1")

# Test case for successfully changing the user perissions to permission_id so passed
def test_admin_permission_change_successful(reset_datastore, three_new_sample_users):
    response = requests.post(f"{url}admin/userpermission/change/v1", 
                        json={'token': three_new_sample_users['sample_token_0'], 
                        'u_id': three_new_sample_users['sample_uid_1'],
                        'permission_id': PERMISSIONS_OWNER})
    assert response.status_code == 200

    response = requests.post(f"{url}admin/userpermission/change/v1", 
                        json={'token': three_new_sample_users['sample_token_1'], 
                        'u_id': three_new_sample_users['sample_uid_2'],
                        'permission_id': PERMISSIONS_OWNER})
    assert response.status_code == 200

# Test case when u_id does not refer to a valid user ~ raises InputError
def test_admin_permission_change_v1_invalid_uid(reset_datastore, three_new_sample_users):
    response = requests.post(f"{url}admin/userpermission/change/v1", 
                        json={'token': three_new_sample_users['sample_token_0'], 
                        'u_id': 123,
                        'permission_id': PERMISSIONS_MEMBER})
    assert response.status_code == InputError.code

# Test case when a global owner is being demoted ~ raises InputError
def test_admin_permission_change_v1_owner_demoted(reset_datastore, three_new_sample_users):
    response = requests.post(f"{url}admin/userpermission/change/v1", 
                        json={'token': three_new_sample_users['sample_token_0'], 
                        'u_id': three_new_sample_users['sample_uid_0'],
                        'permission_id': PERMISSIONS_MEMBER})
    assert response.status_code == InputError.code

# Test case for invalid permission_id ~ raises InputError
def test_admin_permission_change_v1_invalid_permission_id(reset_datastore, three_new_sample_users):
    response = requests.post(f"{url}admin/userpermission/change/v1", 
                    json={'token': three_new_sample_users['sample_token_0'], 
                    'u_id': three_new_sample_users['sample_uid_1'],
                    'permission_id': 3})
    assert response.status_code == InputError.code

# Test case when the user already has the permissions level set 
# to the permission_id ~ raises InputError
def test_admin_permission_change_v1_same_permission(reset_datastore, three_new_sample_users):
    response = requests.post(f"{url}admin/userpermission/change/v1", 
                    json={'token': three_new_sample_users['sample_token_0'], 
                    'u_id': three_new_sample_users['sample_uid_1'],
                    'permission_id': PERMISSIONS_MEMBER})
    assert response.status_code == InputError.code

# Test case when the authorised user amending a user's permissions
# is not even a global owner ~ raises AccessError
def test_admin_permission_change_v1_user_not_owner(reset_datastore, three_new_sample_users):
    response = requests.post(f"{url}admin/userpermission/change/v1", 
                    json={'token': three_new_sample_users['sample_token_1'], 
                    'u_id': three_new_sample_users['sample_uid_2'],
                    'permission_id': PERMISSIONS_MEMBER})
    assert response.status_code == AccessError.code
