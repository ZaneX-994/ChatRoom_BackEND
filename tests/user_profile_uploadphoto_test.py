import pytest
import requests

from src.config import url
from src.error import InputError
from tests.dm_create_test import reset, user0

# 272 x 240 image of a banana
IMAGE = 'http://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/272px-Banana-Single.jpg'
IMAGE_PNG = 'http://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/272px-Banana-Single.png'


# Successful photo upload.
def test_uploadphoto_success(reset, user0):
    result = requests.post(f"{url}user/profile/uploadphoto/v1", json={
        'token': user0['token'],
        'img_url': IMAGE,
        'x_start': 0,
        'y_start': 0,
        'x_end': 272,
        'y_end': 240,
    }).json()
    assert result == {}

    profile_img = requests.get(f"{url}user/profile/v1", params={
        'token': user0['token'],
        'u_id': user0['auth_user_id'],
    }).json()['user']['profile_img_url']
    assert requests.get(profile_img).status_code == 200

# Image url is invalid.
def test_uploadphoto_invalid_url(reset, user0):
    result = requests.post(f"{url}user/profile/uploadphoto/v1", json={
        'token': user0['token'],
        'img_url': IMAGE + 'a',
        'x_start': 0,
        'y_start': 0,
        'x_end': 272,
        'y_end': 240,
    })
    assert result.status_code == InputError.code


# Dimensions not within bounds.
def test_uploadphoto_dimensions_too_big(reset, user0):
    result = requests.post(f"{url}user/profile/uploadphoto/v1", json={
        'token': user0['token'],
        'img_url': IMAGE,
        'x_start': 0,
        'y_start': 0,
        'x_end': 273,
        'y_end': 241,
    })
    assert result.status_code == InputError.code


# Dimensions are invalid.
def test_uploadphoto_dimensions_invalid(reset, user0):
    result = requests.post(f"{url}user/profile/uploadphoto/v1", json={
        'token': user0['token'],
        'img_url': IMAGE,
        'x_start': 0,
        'y_start': 0,
        'x_end': 0,
        'y_end': 0,
    })
    assert result.status_code == InputError.code


# Image is not of JPG format.
def test_uploadphoto_not_jpg(reset, user0):
    result = requests.post(f"{url}user/profile/uploadphoto/v1", json={
        'token': user0['token'],
        'img_url': IMAGE_PNG,
        'x_start': 0,
        'y_start': 0,
        'x_end': 1,
        'y_end': 1,
    })
    assert result.status_code == InputError.code

