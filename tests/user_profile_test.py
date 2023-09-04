import pytest
import requests

from src.config import url
from src.error import InputError
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, auth_register


@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")


def test_user_profile_successful(reset):
    user = auth_register(VALID_EMAIL, VALID_PASSWORD, "John", "Doe")
    result = requests.get(f"{url}user/profile/v1", params={
        'token': user['token'],
        'u_id': user['auth_user_id'],
    }).json()

    # Check user data matches.
    data = result['user']
    assert data['u_id'] == user['auth_user_id']
    assert data['email'] == VALID_EMAIL
    assert data['name_first'] == "John"
    assert data['name_last'] == "Doe"
    assert data['handle_str'] == "johndoe"

    # Check profile image can be retrieved.
    img_url = data['profile_img_url']
    assert requests.get(img_url).status_code == 200


def test_user_profile_invalid_id(reset):
    user = auth_register(VALID_EMAIL, VALID_PASSWORD, "John", "Doe")
    result = requests.get(f"{url}user/profile/v1", params={
        'token': user['token'],
        # Guarantee an invalid user id.
        'u_id': user['auth_user_id'] + 1,
    })
    assert result.status_code == InputError.code

