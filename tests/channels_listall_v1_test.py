# import pytest

# from src.other import clear_v1
# from src.auth import auth_register_v1
# from src.channels import channels_listall_v1, channels_create_v1
# from src.error import AccessError

# VALID_EMAIL_0 = "joe.shmoe@protonmail.com"
# VALID_PASSWORD_0 = "aD1#bl"
# VALID_FIRST_NAME_0 = "Joe"
# VALID_LAST_NAME_0 = "Shmoe"
# VALID_EMAIL_1 = "donkey.kong78@outlook.com"
# VALID_PASSWORD_1 = "banana"
# VALID_FIRST_NAME_1 = "Donkey"
# VALID_LAST_NAME_1 = "Kong"

# @pytest.fixture
# def reset_data_store():
#     clear_v1()

# @pytest.fixture
# def two_new_sample_users():
#     uid_0 = auth_register_v1(VALID_EMAIL_0, VALID_PASSWORD_0, VALID_FIRST_NAME_0, VALID_LAST_NAME_0)
#     uid_1 = auth_register_v1(VALID_EMAIL_1, VALID_PASSWORD_1, VALID_FIRST_NAME_1, VALID_LAST_NAME_1)
#     assert 'auth_user_id' in uid_0
#     assert 'auth_user_id' in uid_1
#     assert type(uid_0['auth_user_id']) == int
#     assert type(uid_1['auth_user_id']) == int
#     # there are 2 valid users in the data_store now^
#     sample_usrs = {
#         'sample_uid_0': uid_0['auth_user_id'],
#         'sample_uid_1': uid_1['auth_user_id'],
#     }
#     return sample_usrs


# def test_unregistered_user_id(reset_data_store):
#     with pytest.raises(AccessError):
#         channels_listall_v1(0)

# def test_invalid_auth_user_id_parameters(reset_data_store):
#     with pytest.raises(AccessError):
#         channels_listall_v1({})
#     with pytest.raises(AccessError):
#         channels_listall_v1(())
#     with pytest.raises(AccessError):
#         channels_listall_v1([])
#     with pytest.raises(AccessError):
#         channels_listall_v1({'auth_user_id': 1},)
#     with pytest.raises(AccessError):
#         channels_listall_v1(-545.2)
#     with pytest.raises(AccessError):
#         channels_listall_v1(456.66)
#     with pytest.raises(AccessError):
#         channels_listall_v1(False)
#     with pytest.raises(AccessError):
#         channels_listall_v1(True)
#     with pytest.raises(AccessError):
#         channels_listall_v1("Bivisdsfjkshdf")
#     with pytest.raises(AccessError):
#         channels_listall_v1("donkey")

# def test_with_empty_channels(reset_data_store, two_new_sample_users):
#     valid_u_id_0 = two_new_sample_users['sample_uid_0']
#     valid_u_id_1 = two_new_sample_users['sample_uid_1']
#     result_0 = channels_listall_v1(valid_u_id_0)
#     result_1 = channels_listall_v1(valid_u_id_1)
#     assert result_0 == result_1 
#     assert type(result_0['channels']) == list
#     assert result_0 == {'channels': [],}

# def test_with_one_and_two_channels(reset_data_store, two_new_sample_users):
#     valid_u_id_0 = two_new_sample_users['sample_uid_0']
#     valid_u_id_1 = two_new_sample_users['sample_uid_1']
#     # No channels exist yet
#     result_0 = channels_listall_v1(valid_u_id_0)
#     assert type(result_0['channels']) == list
#     assert len(result_0['channels']) == 0
#     # Now make one channel
#     channels_create_v1(valid_u_id_0, 'School', True)
#     result_1 = channels_listall_v1(valid_u_id_0)
#     assert type(result_1['channels']) == list
#     assert len(result_1['channels']) == 1           # 'channels' should 1 c_id/name dict.
#     # Make second channel
#     channels_create_v1(valid_u_id_1, 'Family', False)
#     result_2 = channels_listall_v1(valid_u_id_1)
#     assert type(result_2['channels']) == list
#     assert len(result_2['channels']) == 2          # 'channels' should 2 c_id/name dict.

#     # assert result_1 == {'channels': [{}, {}, {}...]}??? == result_2 because it lists ALL channels