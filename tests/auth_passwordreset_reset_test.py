import pytest
import requests

from src.config import url
from tests.auth_register_test import VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME
from src.error import InputError

@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")

@pytest.fixture
def userOne():
    return {
        "email": VALID_EMAIL,
        "password": VALID_PASSWORD,
        "name_first": VALID_FIRST_NAME,
        "name_last": VALID_LAST_NAME,
    }

# test with invalid reset_code
def test_invalid_reset_code(reset, userOne):
    requests.post(f"{url}auth/register/v2", json=userOne)

    reset_result = requests.post(f"{url}auth/passwordreset/reset/v1", json={
        'reset_code': 'anything',
        'new_password': '1newPassWord',
    })

    assert reset_result.status_code == InputError.code

    reset_result = requests.post(f"{url}auth/passwordreset/reset/v1", json={
        'reset_code': 'anything',
        'new_password': '1234',
    })

    assert reset_result.status_code == InputError.code

    
