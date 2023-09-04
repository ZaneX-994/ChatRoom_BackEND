# import pytest

# from src.auth import auth_register_v1
# from src.error import InputError
# from src.error import AccessError
# from src.channel import channel_messages_v1
# from src.channels import channels_create_v1
# from src.other import clear_v1

# VALID_EMAIL = "a@example.com"
# VALID_EMAIL_TWO = "b@example.com"
# VALID_PASSWORD = "password"
# VALID_FIRST_NAME = "John"
# VALID_FIRST_NAME_TWO = "Jim"
# VALID_LAST_NAME = "Doe"
# VALID_LAST_NAME_TWO = "Green"
# VALID_NAME = "channelOne"
# IS_PUBLIC = True

# @pytest.fixture
# def clear():
#     clear_v1()

# def test_channel_messages_invalid_user_id(clear):
#     with pytest.raises(AccessError):
#         channel_messages_v1(1, 1, 0)
        
# def test_channel_messages_invalid_channel_id(clear):
#     user_id = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)['auth_user_id']
#     with pytest.raises(InputError):
#         channel_messages_v1(user_id, 1, 0)

# def test_channel_messages_invalid_start(clear):
#     user_id = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)['auth_user_id']
#     channel_id = channels_create_v1(user_id, VALID_NAME, IS_PUBLIC)['channel_id']
#     with pytest.raises(InputError):
#         channel_messages_v1(user_id, channel_id, 1)

# def test_channel_messages_not_member(clear):
#     user_id1 = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)['auth_user_id']
#     user_id2 = auth_register_v1(VALID_EMAIL_TWO, VALID_PASSWORD, VALID_FIRST_NAME_TWO, VALID_LAST_NAME_TWO)['auth_user_id']
#     channel_id = channels_create_v1(user_id2, VALID_NAME, IS_PUBLIC)['channel_id']
#     with pytest.raises(AccessError):
#         channel_messages_v1(user_id1, channel_id, 0)
    

