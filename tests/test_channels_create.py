# import pytest
# from src.auth import auth_register_v1
# from src.error import InputError, AccessError
# from src.channels import channels_create_v1, channels_list_v1
# from src.other import clear_v1

# VALID_EMAIL = "a@example.com"
# VALID_PASSWORD = "password"
# VALID_FIRST_NAME = "John"
# VALID_LAST_NAME = "Doe"
# VALID_NAME = 'channelOne'
# INVALID_NAME = 'n' * 21
# IS_PUBLIC = True

# @pytest.fixture
# def reset():
#     clear_v1()

# def test_channels_create_with_invalid_name(reset):

#     new_user_id = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)['auth_user_id']
    
#     with pytest.raises(InputError):
#         channels_create_v1(new_user_id, INVALID_NAME, IS_PUBLIC)
#     with pytest.raises(InputError):
#         channels_create_v1(new_user_id, '', IS_PUBLIC)

# def test_channels_create_with_invalid_uid(reset):

#     with pytest.raises(AccessError):
#         channels_create_v1(1, VALID_NAME, IS_PUBLIC)

# def test_channels_create_if_success(reset):

#     new_user_id = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)['auth_user_id']

#     new_channel_id = channels_create_v1(new_user_id, VALID_NAME, IS_PUBLIC)

#     assert 'channel_id' in new_channel_id
#     assert type(new_channel_id['channel_id']) is int

# def test_if_creator_a_member(reset):

#     new_user_id = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)['auth_user_id']

#     new_channel_id = channels_create_v1(new_user_id, VALID_NAME,IS_PUBLIC)['channel_id']

#     channel_list = channels_list_v1(new_user_id)['channels']

#     assert new_channel_id == channel_list[0]['channel_id']