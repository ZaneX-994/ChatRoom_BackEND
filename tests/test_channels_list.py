# import pytest
# from src.auth import auth_register_v1
# from src.error import AccessError
# from src.other import clear_v1
# from src.channels import channels_list_v1, channels_create_v1

# VALID_EMAIL = "a@example.com"
# VALID_PASSWORD = "password"
# VALID_FIRST_NAME = "John"
# VALID_LAST_NAME = "Doe"

# @pytest.fixture
# def reset():
#     clear_v1()

# def test_auth_id_invalid(reset):

#     with pytest.raises(AccessError):
#         channels_list_v1(0)

# def test_zero_channel(reset):

#     new_user = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)
#     channel_list = channels_list_v1(new_user['auth_user_id'])

#     assert not channel_list['channels']

# def test_channel_list_with_one_channel(reset):

#     new_user = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)
#     new_channel = channels_create_v1(new_user['auth_user_id'], 'channelOne', True)
#     channel_list = channels_list_v1(new_user['auth_user_id'])

#     assert channel_list['channels'][0]['name'] == 'channelOne'
#     assert channel_list['channels'][0]['channel_id'] == new_channel['channel_id']

# def test_channel_list_with_several_channels(reset):

#     new_user = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)

#     channels_create_v1(new_user['auth_user_id'], 'channelOne', True)
#     channels_create_v1(new_user['auth_user_id'], 'channelTwo', True)

#     channel_list = channels_list_v1(new_user['auth_user_id'])

#     assert len(channel_list['channels']) == 2
