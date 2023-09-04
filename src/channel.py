from src.data_store import data_store
from src.error import AccessError, InputError
from src.auth import PERMISSIONS_OWNER, PERMISSIONS_MEMBER,extract_validate_token_user_id


def channel_invite_v1(token, channel_id, u_id):
    """
    When provided the correct type of token, channel_id and u_id the function
    invites the user with ID u_id to join a channel with ID channel_id

    Arguments:
    token(str)                - an authorisation hash returned by backend that the 
                                frontend will store and pass into most of the functions                  
    channel_id(int)           - the id of the channel
    u_id(int)                 - the id of the invitee

    Exceptions:
    InputError                - Occurs when channel_id does not refer to a valid channel.
    InputError                - Occurs when u_id does not refer to a valid user
    InputError                - Occurs when u_id refers to a user who is already 
                                a member of the channel
    AccessError               - Occurs when channel_id is valid and the authorised 
                                user is not a member of the channel

    Return Value:
    Returns {}
    """
    check_input_types(token, channel_id)
    db = data_store.get()
    uid = check_ids_are_registered_in_db(token, channel_id, db)
    
    if u_id not in db['users']:
        raise InputError('Invalid user')
    
    channel = db['channels'][channel_id]
    if u_id in channel['members']:
        raise InputError('Invitee is already a member of the channel')
    if uid not in channel['members']:
        raise AccessError('Authorised user is not a member of the channel')
    
    # Add the notification
    handle = db['users'][uid]['handle_str']
    channel_name = db['channels'][channel_id]['name']
    notification_message = f"{handle} added you to {channel_name}"
    db['notifications'][u_id].insert(0,{
        'channel_id': channel_id,
        'dm_id': '-1',
        'notification_message': notification_message
    })

    channel['members'].append(u_id)
    return {}

def channel_details_v1(token, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a member of, 
    the function provides basic details about the channel.

    Arguments:
    token(str)                - an authorisation hash returned by backend that the 
                                frontend will store and pass into most of the functions
    channel_id(int)           - the id of the channel

    Exceptions:
    InputError                - Occurs when channel_id does not refer to a valid channel
    AccessError               - Occurs when channel_id is valid and the authorised user 
                                is not a member of the channel 

    Return Value:
    { name: ...
    is_public: ... 
    owner_members: ... 
    all_members: ... }
    """
    # Helper function to check the data types of token and channel_id
    check_input_types(token, channel_id)

    db = data_store.get()

    # Helper function to check the data types of token and channel_id
    auth_user_id = check_ids_are_registered_in_db(token, channel_id, db)

    # Raise AccessError a non-channel-member tries to access the details 
    # of a certain channel
    if auth_user_id not in db['channels'][channel_id]['members']:
        raise AccessError('Non member accessing the channel details')
    
    channel_dets = db['channels'][channel_id]
    owner_members = []
    all_members = []
    for owner in channel_dets['owners']:
        owner_members.append(db['users'][owner])
    for member in channel_dets['members']:
        all_members.append(db['users'][member])

    return {
        'name': channel_dets['name'],
        'is_public': channel_dets['ispublic'],
        'owner_members': owner_members,
        'all_members': all_members,
    }

def channel_messages_v1(token, channel_id, start):
    '''
    When the user enters the correct token, channel_id and start, the function returns start to end(start + 50), 
    returns all remaining information if less than 50 is left, if the end is recent information return end = -1

    Arguments:
        token (str)           - the token of the user
        channel_id (int)      - the id of the channel
        start (int)           - the number at which the message begins

    Exceptions:
        InputError  - Occurs when token is invalid and start is greater than the total of messages
        AccessError - Occurs when token is invalid and user is not a member of the channel 
    
    Return Value:
        Returns {messages} when token, channel_id and start are valid
            messages is a list of  dictionary that contains {message_id, u_id, message, time_sent}
        Returns start when all is valid
        Returns end when all is valid
    '''
    # check_input_types(token, channel_id)
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    if channel_id not in db['channels']:
        raise InputError("Non-existent channel id")

    message_output_list = []
    messages = db['channels'][channel_id]['messages']
    
    if len(messages) < start:
        raise InputError('Invalid Start')
    
    # check if the user is a member of the channel
    if auth_user_id not in db['channels'][channel_id]['members']:
        raise AccessError('Authorised user is not a member of the channel')
        
    end = start + 50
    # If the remaining information is less than 50, the function returns the the remaining information
    if end >= len(messages):
        for want_id in range(start, len(messages)):
            message_id = messages[want_id]
            for message in db['messages'].values():
                if message_id == message['message_id']:
                    message_output_list.append(message)
        end = -1
    # The funcion returns 50 messages 
    else:
        for want_id in range(start, end):
            message_id = messages[want_id]
            for message in db['messages'].values():
                if message_id == message['message_id']:
                    message_output_list.append(message)

    messages = add_message_reactions(message_output_list, auth_user_id)
    return {
        'messages': list(reversed(messages)),
        'start': start,
        'end': end,
    }


def add_message_reactions(messages: list, u_id):
    """
    Copies and augments the reactions of a list of messages.
    """
    new_messages = []
    for message in messages:
        new_reacts = []
        for react in message['reacts']:
            react = react.copy()
            react['is_this_user_reacted'] = u_id in react['u_ids']
            new_reacts.append(react)

        message = message.copy()
        message['reacts'] = new_reacts
        new_messages.append(message)
    return new_messages


def channel_join_v1(token, channel_id):
    """
    Given a channel_id of a channel that the authorised user's
    token can join, adds them to that channel.

    Arguments:
        token(str)              - the token of whoever it is who is trying to join
                                    the channel with id == channel_id
        channel_id(int)         - the id of the channel

    Exception:
        InputError  - Occurs when:
                        - channel_id does not refer to a valid channel
                        - the authorised user is already a member of the channel

        AccessError - Occurs when channel_id refers to a channel that is private
                        and the authorised user is not already a channel member
                        and is not a global owner

    Return Value:
        Returns {}
    """
    check_input_types(token, channel_id)

    db = data_store.get()
    auth_user_id = check_ids_are_registered_in_db(token, channel_id, db)

    # Channel associated with channel_id may need to be public
    channel_info = db['channels'][channel_id]
    if channel_info['ispublic'] == False and not is_global_owner(db, auth_user_id):
        raise AccessError("You need an invite to join a private channel")
    
    # Must not already be a member
    if auth_user_id in channel_info['members']:
        raise InputError("User is already a member of the channel")
    
    # Otherwise, add them to the channels LIST of members
    channel_info['members'].append(auth_user_id)
    return {}

def channel_leave_v1(token, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a
    member of, remove them as a member of the channel. Their messages
    should remain in the channel. If the only channel owner leaves,
    the channel will remain.

    Arguments:
        token(str)              - the token of whoever it is who is trying to leave
                                    the channel with id == channel_id
        channel_id(int)         - the id of the channel

    Exception:
        InputError  - Occurs when channel_id does not refer to a valid channel

        AccessError - Occurs when channel_id is valid and the authorised
                        user is not a member of the channel

    Return Value:
        Returns {}
    """
    check_input_types(token, channel_id)

    db = data_store.get()
    auth_user_id = check_ids_are_registered_in_db(token, channel_id, db)
    
    channel_info = db['channels'][channel_id]

    # If the auth_user_id belongs to a non-member, it should raise an AccessError...
    if auth_user_id not in channel_info['members']:
        raise AccessError("Non-members can't leave a channel")
    # ...otherwise, remove the user id from the channels list of members
    channel_info['members'].remove(auth_user_id)

    return {}

def channel_addowner_v1(token, channel_id, u_id):
    """
    Make user with user id u_id an owner of the channel.

    Arguments:
        token(str)              - the token of whoever it is who is trying to leave
                                    the channel with id == channel_id
        channel_id(int)         - the id of the channel
        u_id(int)               - the id of the channel

    Exception:
        InputError  - Occurs when:
                        - channel_id does not refer to a valid channel
                        - u_id does not refer to a valid user
                        - u_id refers to a user who is not a member of the channel
                        - u_id refers to a user who is already an owner of the channel

        AccessError - Occurs when channel_id is valid and the authorised user
                        does not have owner permissions in the channel

    Return Value:
        Returns {}
    """
    check_input_types(token, channel_id)
    if type(u_id) is not int:
        raise InputError("Invalid u_id")

    db = data_store.get()
    auth_user_id = check_ids_are_registered_in_db(token, channel_id, db)
    if u_id not in db['users']:
        raise InputError('u_id does not refer to a valid user')
    
    channel_info = db['channels'][channel_id]

    # If the auth_user_id belongs to a non-member, they can't add owners:
    if auth_user_id not in channel_info['owners']:
        raise AccessError('auth_user_id is not authorised to add to this channel')
    # u_id can't become an owner if they are not a channel member or if they already are an owner:
    if u_id not in channel_info['members']:
        raise InputError('u_id refers to a user who is not a member of the channel')
    if u_id in channel_info['owners']:
        raise InputError('u_id refers to a user who is already an owner of the channel')
        
    # ...otherwise, add user's u_id to list of owners
    channel_info['owners'].append(u_id)

    return {}

def check_input_types(token, channel_id):
    """
    Given an token and channel_id, checks whether
    they are the right type

    Arguments:
        token(str)            - an authorisation hash returned by backend that the 
                                frontend will store and pass into most of the functions.
        channel_id(int)       - the id of the channel

    Exception:
        InputError  - Occurs when channel_id is not an int

        AccessError - Occurs when token is not an str
    """
    if type(token) is not str:
        raise AccessError("Invalid token type")
    if type(channel_id) is not int:
        raise InputError("Invalid channel_id type")

def check_ids_are_registered_in_db(token, channel_id, db):
    """
    Given an token, channel_id and a data_store object, checks whether
    they are registered

    Arguments:
        token(int)              - the token of the user directly accessing the channel 
        channel_id(int)         - the id of the channel
        channel_id(dictionary)  - the data_store

    Exception:
        InputError  - Occurs when channel_id does not refer to a valid channel

        AccessError  - Occurs when token does not refer to a valid user

    Return:
        auth_user_id(int)       - the u_id in the token
    """
    auth_user_id = extract_validate_token_user_id(db, token)

    if channel_id not in db['channels']:
        raise InputError("Non-existent channel id")
    
    return auth_user_id

def is_global_owner(db, auth_user_id):
    """
    Checks whether a user is a global owner of Seams.

    Arguments:
        db (dictionary)         - The data store
        auth_user_id (int)      - The id of the user

    Return Value:
        Returns True if the user is a global owner.
    """
    return db['global_permissions'][auth_user_id] == PERMISSIONS_OWNER

def channel_removeowner_v1(token, channel_id, u_id):
    """
    Remove user with user id u_id as an owner of the channel.

    Arguments:
        token(str)              - the token of the user directly accessing the channel 
        channel_id(int)         - the id of the channel
        u_id(int)               - the user_id of target channel owner

    Exception:
        InputError  - Occurs when channel_id does not refer to a valid channel
                    - Occurs when u_id does not refer to a valid user
                    - Occurs when u_id refers to a user who is not an owner of the channel
                    - Occurs when u_id refers to a user who is currently the only owner of the channel
        AccessError - Occurs when channel_id is valid and the authorised user does not have owner permissions 
                        in the channel
    """
    db = data_store.get()
    deleter_uid = check_ids_are_registered_in_db(token, channel_id, db)
    # check for InputError
    if not u_id in db['users'].keys():
        raise InputError('Invalid u_id')
    elif not u_id in db['channels'][channel_id]['owners']:
        raise InputError('user to remove is not an owner')
    elif db['global_permissions'][deleter_uid] == PERMISSIONS_MEMBER or not u_id in db['channels'][channel_id]['owners']:
        # check for AccessError
        raise AccessError('Permission denied')
    elif len(db['channels'][channel_id]['owners']) == 1:
        raise InputError('user to remove is the only owner')
    
    db['channels'][channel_id]['owners'].remove(u_id)

    return {}

