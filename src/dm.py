import time
import re

from src.data_store import data_store
from src.error import InputError, AccessError
from src.auth import extract_validate_token_user_id
from src.channel import add_message_reactions

def dm_create(token, u_ids):
    """
    Creates a new dm.

    Arguments:
        token (string)      - The token of the user
        u_ids (number list) - The list of other users to be added

    Exceptions:
        InputError  - Occurs when the user id is invalid or there are duplicates

    Return Value:
        Returns { dm_id } when successful where dm_id
        is the ID of the new direct messages group.
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)
    
    # Check user ids are valid.
    present_users = set()
    present_users.add(u_id)
    user_handles = [db['users'][u_id]['handle_str']]
    for other_id in u_ids:
        if other_id not in db['users']:
            raise InputError("Invalid user id")
        if other_id in present_users:
            raise InputError("Duplicate user id")

        present_users.add(other_id)
        user_handles.append(db['users'][other_id]['handle_str'])
    
    
    # Create DM.
    dm_id = len(db['dms'])
    db['dms'][dm_id] = {
        'name': construct_dm_name(user_handles),
        'creator_id': u_id,
        'members': list(present_users),
        'messages': [],
        'reacts': [],
        'is_pinned': False,
    }

    # Add the notification
    handle = db['users'][u_id]['handle_str']
    dm_name = db['dms'][dm_id]['name']
    notification_message = f"{handle} added you to {dm_name}"
    for user_id in u_ids:
        db['notifications'][user_id].insert(0, {
            'channel_id': '-1',
            'dm_id': dm_id,
            'notification_message': notification_message
        })
    
    telemetry_dms(db, 1)
    return {
        'dm_id': dm_id,
    }

def dm_list_v1(token):
    """
    Returns the list of DMs that the user is a member of.

    Arguments:
        token (string)      - The token of the user who
                                requested the dm list

    Exceptions: 
        AccessError - Thrown when the token passed in is invalid.

    Return Value:
        Returns { dms } when successful where dms is a list
        of dictionaries, where each dictionary contains
        types { dm_id(int), name(str) }
    """
    db = data_store.get()
    user_id = extract_validate_token_user_id(db, token)
    
    # The following will be a LIST of dictionaries with 'dm_id' & 'name' entries 
    dms_list = []
    for dm_id, dm in db['dms'].items():
        if user_id in dm['members']:
            id_name_pair =  {
                'dm_id': dm_id, 
                'name': dm['name'],
            }
            dms_list.append(id_name_pair)

    return {
        'dms': dms_list,
    }

def construct_dm_name(handles):
    """
    Constructs the name of a new DM.

    Arguments:
        handles (string list)   - The list of all user handles

    Return Value:
        Returns a string representing the DM name.
    """
    handles = sorted(handles)
    return ', '.join(handles)


def senddm(token, dm_id, message):
    """
    Sends a message in a dm.

    Arguments:
        token (string)      - The token of the user who sent the dm
        dm_id (number)      - The ID of the existing dm group
        message (string)    - The message content to be sent

    Exceptions:
        InputError  - Occurs when the dm id is invalid 
        AccessError - Occurs when the user is not in the dm

    Return Value:
        Returns { message_id } when successful where message_id
        is the ID of the new message.
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)
    if dm_id not in db['dms']:
        raise InputError("DM does not exist for this dm_id")

    # Check user is authorized.
    dm = db['dms'][dm_id]
    if u_id not in dm['members']:
        raise AccessError("User does not belong to DM")

    # Validate message length.
    if not (1 <= len(message) <= 1000):
        raise InputError("Message length out of bounds")

    # Add the notification (taggeed)
    handle = db['users'][u_id]['handle_str']
    dm_name = db['dms'][dm_id]['name']
    res = re.compile(r'@+[A-Za-z0-9]*')
    result = set(list(res.findall(message)))
    handle_list = []
    for i in result:
        i = i.replace('@','')
        handle_list.append(i)
    for number_id in db['dms'][dm_id]['members']:
        if db['users'][number_id]['handle_str'] in handle_list:
            notification_message = f"{handle} tagged you in {dm_name}: {message[0:20]}"
            db['notifications'][number_id].insert(0,{
            'channel_id': '-1',
            'dm_id': dm_id,
            'notification_message': notification_message
            })

    # Add message.
    message_id = len(db['messages'])
    dm['messages'].append(message_id)
    db['messages'][message_id] = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_sent': time.time(),
        'reacts': [],
        'is_pinned': False,
    }

    telemetry_messages(db, 1)
    return {
        'message_id': message_id,
    }


def dm_leave(token, dm_id):
    """
    User leave the dm that dm_id refers to

    Arguments:
        token (string)      - The token of the user
        dm_id (int)         - The id of the dm
    Exceptions:
        InputError          - Occurs when dm_id does not refer to a valid DM
        AccessError         - Occurs when dm_id is valid and the authorised user is not a member of the DM
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)
    if dm_id not in db['dms']:
        raise InputError("This is not a valid dm_id")
    elif u_id not in db['dms'][dm_id]['members']:
        raise AccessError("This is not a valid token")
    # remove from dm members
    db['dms'][dm_id]['members'].remove(u_id)

    return {}


def dm_details(token, dm_id):
    """
    get the details of the DM with dm_id that the user is a member of

    Arguments:
        token (string):         - The token of the authorised user
        dm_id (int):            - The id of the DM
    """
    db = data_store.get()
    if dm_id not in db['dms']:
        raise InputError('Invalid dm_id')

    u_id = extract_validate_token_user_id(db, token)
    if not u_id in db['dms'][dm_id]['members']:
        raise AccessError('User is not a member of the DM')

    members = []
    for member in db['dms'][dm_id]['members']:
        members.append(db['users'][member])

    return {
        'name': db['dms'][dm_id]['name'],
        'members': members,
    }


def dm_messages(token, dm_id, start):
    """
    Gets up to 50 messages from a dm.

    Arguments:
        token (string)      - The token of the user who is in the dm
        dm_id (number)      - The ID of the existing dm group
        start (number)      - The index to get messages from

    Exceptions:
        InputError  - Occurs when the dm id is invalid or when start
                        is greater than the number of messages available
        AccessError - Occurs when the user is not in the dm

    Return Value:
        Returns { messages, start, end } when successful where 
        messages is the list of messages, start is the same
        as the argument, and end which is start + 50 if there
        are more messages remaining or -1 otherwise.
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)
    if dm_id not in db['dms']:
        raise InputError("DM does not exist for this dm_id")

    # Check user is authorized.
    dm = db['dms'][dm_id]
    if u_id not in dm['members']:
        raise AccessError("User does not belong to DM")

    # Get messages.
    end = start + 50
    end_index = len(dm['messages']) - start
    start_index = len(dm['messages']) - end

    if end_index < 0:
        # Start index out of bounds.
        raise InputError("Start index out of bounds")

    if start_index <= 0:
        # No more remaining messages.
        start_index = 0
        end = -1

    messages = []
    for message_id in reversed(dm['messages'][start_index:end_index]):
        messages.append(db['messages'][message_id])
    messages = add_message_reactions(messages, u_id)

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }

def dm_remove(token, dm_id):
    """
    Attempts to remove the DM that dm_id refers to

    Arguments:
        token (string)      - The token of the creator of the dm
        dm_id (number)      - The ID of the existing dm group

    Exceptions:
        InputError  - Occurs when dm_id does not refer to a valid DM

        AccessError - Occurs when dm_id is valid and the authorised user is not the original DM creator
                    - Occurs when dm_id is valid and the authorised user is no longer in the DM
    """
    db = data_store.get()
    # check for InputError
    if dm_id not in db['dms']:
        raise InputError("Invalid dm_id")

    u_id = extract_validate_token_user_id(db, token)
    # check for AccessError
    if u_id != db['dms'][dm_id]['creator_id']:
        raise AccessError("User is not the creator")
    elif u_id not in db['dms'][dm_id]['members']:
        raise AccessError("User not a member anymore")
    
    db['dms'].pop(dm_id)
    telemetry_dms(db, -1)
    return {}


def telemetry_dms(db, delta: int):
    dms_exist = db['workspace_stats']['dms_exist']
    num_dms_exist = dms_exist[-1]['num_dms_exist']
    dms_exist.append({
        'num_dms_exist': num_dms_exist + delta,
        'time_stamp': int(time.time()),
    })


def telemetry_messages(db, delta: int):
    messages_exist = db['workspace_stats']['messages_exist']
    num_messages_exist = messages_exist[-1]['num_messages_exist']
    messages_exist.append({
        'num_messages_exist': num_messages_exist + delta,
        'time_stamp': int(time.time()),
    })


