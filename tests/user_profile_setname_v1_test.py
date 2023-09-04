import pytest
import requests

from src.config import url
from src.user import set_name
from src.error import InputError
from tests.channel_invite_v2_test import three_new_sample_users

SMALL_NAME = ''
LARGE_NAME = 'poqhrkjstheplawnhdgfrtzhizihangwaturdurayangsarthak'

@pytest.fixture
def reset_datastore():
    requests.delete(f"{url}clear/v1")

# Test case for successfully setting the user's first and last name as specified
def test_user_profile_setname_successful(reset_datastore, three_new_sample_users):
    response = requests.put(f"{url}user/profile/setname/v1",
                            json = {'token': three_new_sample_users['sample_token_0'],
                                    'name_first': "slam",
                                    'name_last': 'dunk'}).json()
    assert response == {}

# Test case for very-small first name / Out of bounds
def test_user_profile_setname_firstname_small(reset_datastore, three_new_sample_users):
    response = requests.put(f"{url}user/profile/setname/v1",
                            json = {'token': three_new_sample_users['sample_token_0'],
                                    'name_first': SMALL_NAME,
                                    'name_last': 'dunk'})
    assert response.status_code == InputError.code

# Test case for very-big first name / Out of bounds
def test_user_profile_setname_firstname_large(reset_datastore, three_new_sample_users):
    response = requests.put(f"{url}user/profile/setname/v1",
                            json = {'token': three_new_sample_users['sample_token_0'],
                                    'name_first': LARGE_NAME,
                                    'name_last': 'dunk'})
    assert response.status_code == InputError.code

# Test case for very-small last name / Out of bounds
def test_user_profile_setname_lastname_small(reset_datastore, three_new_sample_users):
    response = requests.put(f"{url}user/profile/setname/v1",
                            json = {'token': three_new_sample_users['sample_token_0'],
                                    'name_first': 'Joe',
                                    'name_last': SMALL_NAME})
    assert response.status_code == InputError.code

# Test case for very-big last name / Out of bounds
def test_user_profile_setname_lastname_large(reset_datastore, three_new_sample_users):
    response = requests.put(f"{url}user/profile/setname/v1",
                            json = {'token': three_new_sample_users['sample_token_0'],
                                    'name_first': 'Joe',
                                    'name_last': LARGE_NAME})
    assert response.status_code == InputError.code

