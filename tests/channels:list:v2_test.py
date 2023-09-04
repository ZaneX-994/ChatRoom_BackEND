# from urllib import response
# from flask import config
# import requests
# from src.config import url 
# import pytest


# # VVALID_EMAIL = "a@example.com"
# # VALID_PASSWORD = "password"
# # VALID_FIRST_NAME = "John"
# # VALID_LAST_NAME = "Doe"
# userOne = {
#     'email': "a@example.com",
#     'password': "password",
#     'name_fist': "John",
#     'name_last': "Doe",
# }
# userTwo = {
#     'email': 'b@example.com',
#     'password': 'password1',
#     'name_first': 'George',
#     'name_last': 'Cooperr'
# }
# VALID_NAME = 'channelOne'
# IS_PUBLIC = True
# INVALID_NAME = 'n' * 21

# @pytest.fixture()
# def reset():
#     requests.delete(url + 'clear/v1')

# @pytest.fixture()
# def newUser1():
#     User = requests.post(url + 'auth/register/v2', json=userOne)
#     return User

# @pytest.fixture()
# def newUser2():
#     User = requests.post(url + 'auth/register/v2', json=userTwo)

# # test for user not in any channel
# def test_user_in_no_channel(reset, newUser1, newUser2):
#     # login or not ?

#     token1 = newUser1.json['token']

#     token2 = newUser2.json['token']

#     new_channel = requests.post(url + 'channels/create/v2', json={
#         'token': token2,
#         'name': VALID_NAME,
#         'is_public': IS_PUBLIC,
#     })

#     list1 = requests.get(url + 'channels/list/v2', params={'token':token1})

#     assert list1.json['channels'] == []
#     assert list1.status_code == 200




