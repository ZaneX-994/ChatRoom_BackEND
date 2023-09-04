# import pytest

# from src.other import clear_v1
# from src.channels import channels_create_v1, channels_listall_v1
# from src.channel import channel_join_v1, channel_details_v1
# from src.auth import auth_register_v1
# from src.error import InputError, AccessError

# VALID_EMAIL_0 = "joe.shmoe@gmail.com"
# VALID_PASSWORD_0 = "aD1#bl"
# VALID_FIRST_NAME_0 = "Joe"
# VALID_LAST_NAME_0 = "Shmoe"
# VALID_EMAIL_1 = "donkey.kong78@outlook.com"
# VALID_PASSWORD_1 = "banana"
# VALID_FIRST_NAME_1 = "Donkey"
# VALID_LAST_NAME_1 = "Kong"
# VALID_EMAIL_2 = "bg@gmail.com"
# VALID_PASSWORD_2 = "A|1ve!"
# VALID_FIRST_NAME_2 = "Bee"
# VALID_LAST_NAME_2 = "Gees"

# @pytest.fixture
# def reset_data_store():
#     clear_v1()

# @pytest.fixture
# def three_new_sample_users():
#     uid_0 = auth_register_v1(VALID_EMAIL_0, VALID_PASSWORD_0, VALID_FIRST_NAME_0, VALID_LAST_NAME_0)
#     uid_1 = auth_register_v1(VALID_EMAIL_1, VALID_PASSWORD_1, VALID_FIRST_NAME_1, VALID_LAST_NAME_1)
#     uid_2 = auth_register_v1(VALID_EMAIL_2, VALID_PASSWORD_2, VALID_FIRST_NAME_2, VALID_LAST_NAME_2)
#     assert 'auth_user_id' in uid_0
#     assert 'auth_user_id' in uid_1
#     assert 'auth_user_id' in uid_2
#     assert type(uid_0['auth_user_id']) == int
#     assert type(uid_1['auth_user_id']) == int
#     assert type(uid_2['auth_user_id']) == int
#     # there are 3 valid users in the data_store now^
#     sample_usrs = {
#         'sample_uid_0': uid_0['auth_user_id'],
#         'sample_uid_1': uid_1['auth_user_id'],
#         'sample_uid_2': uid_2['auth_user_id'],
#     }
#     return sample_usrs

# @pytest.fixture
# def new_u_and_ch_id(three_new_sample_users):
#     user = three_new_sample_users['sample_uid_0']
#     return {
#         "u_id": user,
#         "ch_id": channels_create_v1(user, 'New Channel', True)['channel_id'],
#     }

# # Requires channel_details_v1 to pass 
# def test_users_joins_new_public_channel(reset_data_store, three_new_sample_users):
#     # Have first user make a channel, and that they are it's only member:
#     teacher = three_new_sample_users['sample_uid_0']
#     school_channel = channels_create_v1(teacher, 'School', True)['channel_id']
#     assert type(school_channel) == int
#     result = channels_listall_v1(teacher)['channels'][0]
#     assert result['channel_id'] == school_channel
#     assert result['name'] == 'School'
#     school_ch_members_1 = channel_details_v1(teacher, school_channel)['all_members']
#     assert type(school_ch_members_1) == list
#     assert len(school_ch_members_1) == 1  
#     assert school_ch_members_1[0]['u_id'] == teacher

#     # Now a second user will join the 'School' channel, becoming its second member:
#     student_1 = three_new_sample_users['sample_uid_1']
#     channel_join_v1(student_1, school_channel)
#     school_ch_members_2 = channel_details_v1(student_1, school_channel)['all_members']
#     assert type(school_ch_members_2) == list
#     assert len(school_ch_members_2) == 2 
#     assert school_ch_members_2[0]['u_id'] == teacher
#     assert school_ch_members_2[1]['u_id'] == student_1

#     # Now a second user will join the 'School' channel, becoming its second member:
#     student_2 = three_new_sample_users['sample_uid_2']
#     channel_join_v1(student_2, school_channel)
#     school_ch_members_3 = channel_details_v1(student_2, school_channel)['all_members']
#     assert type(school_ch_members_3) == list
#     assert len(school_ch_members_3) == 3
#     assert school_ch_members_3[0]['u_id'] == teacher
#     assert school_ch_members_3[1]['u_id'] == student_1
#     assert school_ch_members_3[2]['u_id'] == student_2

# def test_global_owner_joins_private_channel(reset_data_store, three_new_sample_users):
#     # Global owner is first user registered.
#     global_owner = three_new_sample_users['sample_uid_0']
#     student_1 = three_new_sample_users['sample_uid_1']
#     school_channel = channels_create_v1(student_1, 'General', False)['channel_id']
#     channel_join_v1(global_owner, school_channel)

# # Requires channel_details_v1 to pass 
# def test_user_tries_to_join_private_channel(reset_data_store, three_new_sample_users):
#     # Have first user make a new private channel
#     teacher = three_new_sample_users['sample_uid_0']
#     staff_channel = channels_create_v1(teacher, 'Staff', False)['channel_id']
#     assert type(staff_channel) == int
#     result = channels_listall_v1(teacher)['channels'][0]
#     assert result['channel_id'] == staff_channel
#     assert result['name'] == 'Staff'
#     staff_ch_members_before = channel_details_v1(teacher, staff_channel)['all_members']
#     assert type(staff_ch_members_before) == list
#     assert len(staff_ch_members_before) == 1
#     assert staff_ch_members_before[0]['u_id'] == teacher

#     # Another user (even if they are registered) cannot join the private channel on their own:
#     student_1 = three_new_sample_users['sample_uid_1']
#     with pytest.raises(AccessError):
#         channel_join_v1(student_1, staff_channel)
#     student_2 = three_new_sample_users['sample_uid_2']
#     with pytest.raises(AccessError):
#         channel_join_v1(student_2, staff_channel)
#     staff_ch_members_after = channel_details_v1(teacher, staff_channel)['all_members']
#     assert type(staff_ch_members_after) == list                 # Nothing should have changed here
#     assert len(staff_ch_members_after) == 1                     #
#     assert staff_ch_members_after == staff_ch_members_before    #

# def test_nonexistant_channel_id(reset_data_store, three_new_sample_users): 
#     user = three_new_sample_users['sample_uid_0']
#     current_channels = channels_listall_v1(user)['channels']
#     assert len(current_channels) == 0       # no channels exist yet
#     with pytest.raises(InputError):
#         channel_join_v1(user, 0)

# def test_unregistered_auth_user_id(reset_data_store, new_u_and_ch_id):
#     unregistered_id = new_u_and_ch_id['u_id'] + 10
#     with pytest.raises(AccessError):
#         channel_join_v1(unregistered_id, new_u_and_ch_id['ch_id'])

# def test_user_already_member(reset_data_store, three_new_sample_users):
#     user_0 = three_new_sample_users['sample_uid_0']
#     new_channel = channels_create_v1(user_0, 'New Channel', True)['channel_id']
#     with pytest.raises(InputError):
#         channel_join_v1(user_0, new_channel)
#     user_1 = three_new_sample_users['sample_uid_1']
#     channel_join_v1(user_1, new_channel)
#     with pytest.raises(InputError):
#         channel_join_v1(user_1, new_channel)
#     user_2 = three_new_sample_users['sample_uid_2']
#     channel_join_v1(user_2, new_channel)
#     with pytest.raises(InputError):
#         channel_join_v1(user_2, new_channel)

# def test_invalid_auth_user_id_types(reset_data_store, three_new_sample_users, new_u_and_ch_id):
#     with pytest.raises(AccessError):
#         channel_join_v1(str(new_u_and_ch_id['u_id']), new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1("bonk", new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1(20.434, new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1(65.76854**2, new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1(True, new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1(False, new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1([], new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1({}, new_u_and_ch_id['ch_id'])
#     with pytest.raises(AccessError):
#         channel_join_v1((), new_u_and_ch_id['ch_id'])

# def test_invalid_channel_id_types(reset_data_store, three_new_sample_users, new_u_and_ch_id):
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], str(new_u_and_ch_id['ch_id']))
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], "&768sdah")
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], 85435.4)
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], 454.75424**2)
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], True)
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], False)
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], [])
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], {})
#     with pytest.raises(InputError):
#         channel_join_v1(new_u_and_ch_id['u_id'], ())

# def test_returns_empty_dict(reset_data_store, three_new_sample_users, new_u_and_ch_id):
#     new_user = three_new_sample_users['sample_uid_1']
#     assert channel_join_v1(new_user, new_u_and_ch_id['ch_id']) == {}

# def test_empty_data_store(reset_data_store): 
#     with pytest.raises(AccessError):
#         channel_join_v1(0, 0)
#     with pytest.raises(AccessError):
#         channel_join_v1(12, 6)
