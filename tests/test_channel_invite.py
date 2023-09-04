# from multiprocessing.spawn import import_main_path
# import pytest
# from src.error import InputError, AccessError
# from src.auth import auth_register_v1
# from src.other import clear_v1
# from src.channels import channels_create_v1
# from src.channel import channel_invite_v1

# VALID_EMAIL_1 = "a@example.com"
# VALID_PASSWORD_1 = "password"
# VALID_FIRST_NAME_1 = "John"
# VALID_LAST_NAME_1 = "Doe"

# VALID_EMAIL_2 = "j@example.com"
# VALID_PASSWORD_2 = "pass123"
# VALID_FIRST_NAME_2 = "Jack"
# VALID_LAST_NAME_2 = "Smith"

# VALID_EMAIL_3 = "k@example.com"
# VALID_PASSWORD_3 = "pass123"
# VALID_FIRST_NAME_3 = "Jack"
# VALID_LAST_NAME_3 = "Smith"

# U_ID = 19035

# @pytest.fixture
# def reset():
#     clear_v1()

# def test_channel_invite_invalid_channel_id(reset):
#     new_user1 = auth_register_v1(VALID_EMAIL_1, VALID_PASSWORD_1, VALID_FIRST_NAME_1, 
#                                 VALID_LAST_NAME_1)
#     new_user2 = auth_register_v1(VALID_EMAIL_2, VALID_PASSWORD_2, VALID_FIRST_NAME_2, 
#                                 VALID_LAST_NAME_2)

#     with pytest.raises(InputError):
#         channel_invite_v1(new_user1['auth_user_id'], 'new@1', new_user2['auth_user_id'])

# def test_channel_invite_ivalid_user_u_id(reset):
    
#     new_user = auth_register_v1(VALID_EMAIL_1, VALID_PASSWORD_1, VALID_FIRST_NAME_1,
#                                 VALID_LAST_NAME_1)
#     new_channel = channels_create_v1(new_user['auth_user_id'], 'new_channel1', False)

#     with pytest.raises(InputError):
#         channel_invite_v1(new_user['auth_user_id'], new_channel['channel_id'], 'inv_uid')
#     with pytest.raises(InputError):
#         channel_invite_v1(new_user['auth_user_id'], new_channel['channel_id'], U_ID)
                                        
# def test_channel_invite_existing_user(reset):
#     new_user1 = auth_register_v1(VALID_EMAIL_1, VALID_PASSWORD_1, VALID_FIRST_NAME_1,
#                                 VALID_LAST_NAME_1)
    
#     new_user2 = auth_register_v1(VALID_EMAIL_2, VALID_PASSWORD_2, VALID_FIRST_NAME_2, 
#                                 VALID_LAST_NAME_2)

#     new_channel = channels_create_v1(new_user1['auth_user_id'], 'new_channel1', False)
    
#     channel_invite_v1(new_user1['auth_user_id'], new_channel['channel_id'], new_user2['auth_user_id'])
#     with pytest.raises(InputError):
#         channel_invite_v1(new_user1['auth_user_id'], new_channel['channel_id'], new_user2['auth_user_id'])

# def test_channel_invite_auth_id_not_member(reset):
#     new_user1 = auth_register_v1(VALID_EMAIL_1, VALID_PASSWORD_1, VALID_FIRST_NAME_1,
#                                 VALID_LAST_NAME_1)
#     new_user2 = auth_register_v1(VALID_EMAIL_2, VALID_PASSWORD_2, VALID_FIRST_NAME_2, 
#                                 VALID_LAST_NAME_2)
#     new_user3 = auth_register_v1(VALID_EMAIL_3, VALID_PASSWORD_2, VALID_FIRST_NAME_2, 
#                                 VALID_LAST_NAME_2)
#     new_channel = channels_create_v1(new_user1['auth_user_id'], 'new_channel1', False)
#     with pytest.raises(AccessError):
#         channel_invite_v1(new_user3['auth_user_id'], new_channel['channel_id'], new_user2['auth_user_id'])        
