import pytest
import requests

from src.config import url
from src.auth import generate_handle
from src.error import InputError


VALID_EMAIL = "a@example.com"
VALID_PASSWORD = "password"
VALID_FIRST_NAME = "John"
VALID_LAST_NAME = "Doe"


@pytest.fixture
def reset():
    requests.delete(f"{url}clear/v1")


def auth_register(email, password, name_first, name_last):
    """
    Helper function for issuing an authentication request.
    """

    result = requests.post(f"{url}auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last,
    })
    print(result)
    if result.status_code == InputError.code:
        raise InputError
    return result.json()


def test_auth_register_valid(reset):
    result = auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)
    assert 'auth_user_id' in result
    assert 'token' in result
    assert type(result['auth_user_id']) == int


def test_auth_register_invalid_email(reset):
    email = "123"
    with pytest.raises(InputError):
        auth_register(email, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

def test_auth_register_duplicate_email(reset):
    auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)
    with pytest.raises(InputError):
        auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

def test_auth_register_tiny_password(reset):
    password = "12345"
    with pytest.raises(InputError):
        auth_register(VALID_EMAIL, password, VALID_FIRST_NAME, VALID_LAST_NAME)


def test_auth_register_invalid_first_name(reset):
    with pytest.raises(InputError):
        auth_register(VALID_EMAIL, VALID_PASSWORD, "", VALID_LAST_NAME)
    with pytest.raises(InputError):
        auth_register(VALID_EMAIL, VALID_PASSWORD, "a" * 51, VALID_LAST_NAME)


def test_auth_register_invalid_last_name(reset):
    with pytest.raises(InputError):
        auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, "")
    with pytest.raises(InputError):
        auth_register(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, "a" * 51)


def test_generate_handle():
    handle_str = generate_handle({}, 'John', 'Doe')
    assert handle_str == 'johndoe'


def test_generate_handle_long():
    handle_str = generate_handle({}, 'A' * 20, 'B' * 10)
    assert handle_str == 'a' * 20


# Check discriminants are added correctly.
def test_generate_handle_discriminant():
    handles = {}
    handle_a = generate_handle(handles, 'John', 'Doe')
    handles[handle_a] = '0'

    handle_b = generate_handle(handles, 'John', 'Doe')
    assert handle_b == 'johndoe0'


# Check handles are only alphanumeric.
def test_generate_handle_non_alphanumeric():
    handle_str = generate_handle({}, 'Jo!hn_0', '😃Doe')
    assert handle_str == 'john0doe'

