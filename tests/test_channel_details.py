# import pytest
# from src.error import InputError, AccessError
# from src.other import clear_v1
# from src.auth import auth_register_v1
# from src.channels import channels_create_v1
# from src.channel import channel_details_v1

# VALID_EMAIL = "a@example.com"
# VALID_PASSWORD = "password"
# VALID_FIRST_NAME = "John"
# VALID_LAST_NAME = "Doe"

# VALID_EMAIL_2 = "j@example.com"
# VALID_PASSWORD_2 = "pass123"
# VALID_FIRST_NAME_2 = "Jack"
# VALID_LAST_NAME_2 = "Smith"

# AUTH_ID_INV = 45089
# CHANNEL_ID_INV = 19023

# @pytest.fixture
# def reset():
#     clear_v1()

# # Check the channel details function returns the correct type.
# def test_channel_details_successful(reset):
#     new_user = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME)
#     new_channel = channels_create_v1(new_user['auth_user_id'], 'new_channel', True)
#     details = channel_details_v1(new_user['auth_user_id'], new_channel['channel_id'])

#     user = details['all_members'][0]
#     keys = ['u_id', 'email', 'name_first', 'name_last', 'handle_str']
#     assert sorted(user.keys()) == sorted(keys)
    

# def test_channel_details_authid_wrongtype(reset):
#     new_user = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, 
#                                 VALID_LAST_NAME)
#     new_channel = channels_create_v1(new_user['auth_user_id'], 'new_channel', True)

#     with pytest.raises(AccessError):
#         channel_details_v1(AUTH_ID_INV, new_channel['channel_id'])
    
# def test_channel_details_channelid_wrongtype(reset):
#     new_user = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, 
#                                 VALID_LAST_NAME)
#     channels_create_v1(new_user['auth_user_id'], 'new_channel', True)
#     with pytest.raises(InputError):
#         channel_details_v1(new_user['auth_user_id'], 'invalid@98')
        
# def test_channel_details_invalid_channel(reset):
#     new_user = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, 
#                                 VALID_LAST_NAME)
#     channels_create_v1(new_user['auth_user_id'], 'new_channel', True)
#     with pytest.raises(InputError):
#         channel_details_v1(new_user['auth_user_id'], CHANNEL_ID_INV)

# def test_channel_details_auth_id_invalid(reset):
#     new_user_1 = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, 
#                             VALID_LAST_NAME)
#     new_channel = channels_create_v1(new_user_1['auth_user_id'], 'new_channel', True)
#     with pytest.raises(AccessError):
#         channel_details_v1(AUTH_ID_INV, new_channel['channel_id'])

# def test_channel_details_auth_id_not_member(reset):
#     new_user_1 = auth_register_v1(VALID_EMAIL, VALID_PASSWORD, VALID_FIRST_NAME, 
#                                 VALID_LAST_NAME)
#     new_user_2 = auth_register_v1(VALID_EMAIL_2, VALID_PASSWORD_2, VALID_FIRST_NAME_2, 
#                                 VALID_LAST_NAME_2)
#     new_channel = channels_create_v1(new_user_1['auth_user_id'], 'new_channel', True)
#     with pytest.raises(AccessError):
#         channel_details_v1(new_user_2['auth_user_id'], new_channel['channel_id'])
