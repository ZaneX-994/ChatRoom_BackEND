import re
import time
import jwt
import datetime
import threading
from datetime import timezone

from src.channel import check_input_types
from src.data_store import data_store
from src.error import AccessError, InputError
from src.auth import extract_validate_token_user_id, PERMISSIONS_OWNER
from src.dm import senddm

VALID_REACT_ID = [1, 2]

def message_send_v1(token, channel_id, message):
    '''
    When the user enters the correct token, channel_id and message, the function returns message_id. 

    Arguments:
        token (str)           - the token of the user
        channel_id (int)      - the id of the channel
        message (str)         - the message send by the user

    Exceptions:
        InputError  - Occurs when channl_id is not valid and length is big or small
        AccessError - Occurs when token is invalid and user is not a member of the channel 
    
    Return Value:
        Returns {message_id} when token, channel_id and message are valid
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    
    if channel_id not in db['channels']:
        raise InputError("Non-existent channel id")
    
    messages = db['channels'][channel_id]['messages']
    if len(message) < 1 or len(message) > 1000:
        raise InputError('Invalid length of message')
    if auth_user_id not in db['channels'][channel_id]['members']:
        raise AccessError('Authorised user is not a member of the channel')
    
    message_id = len(db['messages'])
    messages.append(message_id)

    # Add the notification (taggeed)
    handle = db['users'][auth_user_id]['handle_str']
    channel_name = db['channels'][channel_id]['name']

    res = re.compile(r'@+[A-Za-z0-9]*')
    result = set(list(res.findall(message)))
    handle_list = []
    for i in result:
        i = i.replace('@','')
        handle_list.append(i)

    for number_id in db['channels'][channel_id]['members']: 
       if db['users'][number_id]['handle_str'] in handle_list:
        notification_message = f"{handle} tagged you in {channel_name}: {message[0:20]}"
        db['notifications'][number_id].insert(0,{
        'channel_id': channel_id,
        'dm_id': '-1',
        'notification_message': notification_message
        })
            
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo = timezone.utc)
    utc_timestamp = utc_time.timestamp()

    db['messages'][message_id] = {
        'message': message,
        'u_id': auth_user_id,
        'message_id': message_id,
        'time_sent': utc_timestamp,
        'reacts': [],
        'is_pinned': False,
    }

    telemetry_messages(db, 1)
    return {
        'message_id': message_id
    }

def message_edit_v1(token, message_id, message):
    '''
    When the user enters the correct token, message_id and message, if the message is 
    an empty string, remove the message, otherwise update the text with new text

    Arguments:
        token (str)           - the token of the user
        message_id (int)      - the id of the message
        message (str)         - the message edit by user

    Exceptions:
        InputError  - Occurs when user is not valid and message is too long
        AccessError - Occurs when user is not authorised user or owner 
    
    Return Value:
        Returns {} 
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    check_uid_for_correct_channel(auth_user_id, message_id, db)
    check_user_correct(auth_user_id, message_id, db)

    if len(message) > 1000:
        raise InputError('Invalid length of message')
    
    if not message_id in [msgid for ch in db['channels'].values() for msgid in ch['messages']] \
    and not message_id in [msgid for ch in db['dms'].values() for msgid in ch['messages']]:
        raise InputError('Invalid message_id')

    for channel_ids in db['channels'].values():
        for mess_id in channel_ids['messages']:
            if message_id == mess_id:
                if len(message) == 0:
                    channel_ids['messages'].remove(mess_id)
                else:
                    for mess in db['messages'].values():
                        if mess['message_id'] == message_id:
                            mess['message'] = message


    for channel_ids in db['dms'].values():
        for mess_id in channel_ids['messages']:
            if message_id == mess_id:
                if len(message) == 0:
                    channel_ids['messages'].remove(mess_id)
                else:
                    for mess in db['messages'].values():
                        if mess['message_id'] == message_id:
                            mess['message'] = message

    return {}

def message_remove_v1(token, message_id):
    '''
    When the user enters the correct token, message_id, remove the message with message_id

    Arguments:
        token (str)           - the token of the user
        message_id (int)      - the id of the message

    Exceptions:
        InputError  - Occurs when user is not valid(not a member of channle/dm)
        AccessError - Occurs when user is not authorised user or owner 
    
    Return Value:
        Returns {} 
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    check_uid_for_correct_channel(auth_user_id, message_id, db)
    check_user_correct(auth_user_id, message_id, db)

    if not is_valid_message_id(db, message_id):
        raise InputError('Invalid message_id')
    
    for channel_id in db['channels'].values():
        if message_id in channel_id['messages']:
            channel_id['messages'].remove(message_id)
    for dm_id in db['dms'].values():
        if message_id in dm_id['messages']:
            dm_id['messages'].remove(message_id)

    # Do not remove message directly from data_store as we rely
    # on the number of entries for generating message_ids. 
    telemetry_messages(db, -1)
    return {}


def is_valid_message_id(db, message_id):
    for ch in db['channels'].values():
        if message_id in ch['messages']:
            return True
    for dm in db['dms'].values():
        if message_id in dm['messages']:
            return True
    return False


def check_uid_for_correct_channel(auth_user_id, message_id, db):
    '''
    check the user is or not channel/dm member

    Arguments:
        auth_user_id (int)    - the id of the user
        message_id (int)      - the id of the message
        db (dictionary)       - data

    Exceptions:
        InputError  - Occurs when user is not member
    
    Return Value:
        Returns {} 
    '''
    for channel_num in db['channels'].values():
        if message_id in channel_num['messages']:
            if auth_user_id not in channel_num['members']:
                raise InputError('Authorised user is not a member of the channel')

    for dm_num in db['dms'].values():
        if message_id in dm_num['messages']:
            if auth_user_id not in dm_num['members']:
                raise InputError('Authorised user is not a member of the dm')

def check_user_correct(auth_user_id, message_id, db):
    '''
    check the user is or not owners or authorised

    Arguments:
        auth_user_id (int)    - the id of the user
        message_id (int)      - the id of the message
        db (dictionary)       - data

    Exceptions:
        InputError  - Occurs when user is not owners or authorised
    
    Return Value:
        Returns {} 
    '''
    for mess_id in db['messages'].values():
        if message_id == mess_id['message_id']:
            if auth_user_id == mess_id['u_id']:
                return None

    for channels_id in db['channels'].values():
        if message_id in channels_id['messages']:
            if auth_user_id in channels_id['owners']:
                return None

    for dms_id in db['dms'].values():
        if message_id in dms_id['messages']:
            if auth_user_id == dms_id['creator_id']:
                return None

    if db['global_permissions'][auth_user_id] == PERMISSIONS_OWNER:
        return None

    raise AccessError('The request is not from owners or permissions owners')

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Send the message to the channel at a specified time in the future.

    Arguments:
        token (str)         - the token of the user
        channel_id (int)    - the id of the channel
        message (str)       - the message
        time_sent(int)      - the timestamp

    Exceptions:
        InputError  - Occurs when channel_id is invalid
                    - Occurs when message length is invalid
                    - Occurs when time_sent is invalid

    Return Value:
        Returns {message_id} when token, channel_id, message and time_sent are valid
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    
    if channel_id not in db['channels']:
        raise InputError("Non-existent channel id")
    
    if len(message) < 1 or len(message) > 1000:
        raise InputError("Invalid message length")
    
    if auth_user_id not in db['channels'][channel_id]['members']:
        raise AccessError('Authorised user is not a member of the channel')
    
    message_id = len(db['messages'])
    
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo = timezone.utc)
    time_now = utc_time.timestamp()

    if time_sent <= time_now:
        raise InputError('Invalid time')

    # Send message at a specified time in the future
    send_message = threading.Timer(time_sent - time_now, send_message_channel, args = [db, channel_id, message_id])
    send_message.start()

    db['messages'][message_id] = {
        'message': message,
        'u_id': auth_user_id,
        'message_id': message_id,
        'time_sent': time_sent,
        'reacts': [],
        'is_pinned': False,
    }

    return {
        'message_id': message_id
    }

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Send the message to the dm at a specified time in the future.

    Arguments:
        token (str)         - the token of the user
        dm_id (int)         - the id of the dm
        message (str)       - the message
        time_sent(int)      - the timestamp

    Exceptions:
        InputError  - Occurs when dm_id is invalid
                    - Occurs when message length is invalid
                    - Occurs when time_sent is invalid

    Return Value:
        Returns {message_id} when token, dm_id, message and time_sent are valid
    '''
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)

    if dm_id not in db['dms']:
        raise InputError("DM does not exist for this dm_id")

    if not (1 <= len(message) <= 1000):
        raise InputError("Message length out of bounds")

    dm = db['dms'][dm_id]
    if u_id not in dm['members']:
        raise AccessError("User does not belong to DM")

    message_id = len(db['messages'])
    time_now = time.time()

    if time_sent <= time_now:
        raise InputError('Invalid time')

    # Send message at a specified time in the future
    send_message = threading.Timer(time_sent - time_now, send_message_dm, args = [db, dm_id, message_id])
    send_message.start()

    db['messages'][message_id] = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_sent': time_sent,
        'reacts': [],
        'is_pinned': False,
    }

    return {
        'message_id': message_id
    }

def send_message_channel(db, channel_id, message_id):
    '''
    Send message to the channel

    Arguments:
        db (dictionary)       - data
        channel_id (int)      - the id of the channel
        message_id (int)      - the id of the message
    '''
    db['channels'][channel_id]['messages'].append(message_id)   
    telemetry_messages(db, 1)

def send_message_dm(db, dm_id, message_id):
    '''
    Send message to the dm

    Arguments:
        db (dictionary)       - data
        dm_id (int)           - the id of the dm
        message_id (int)      - the id of the message
    '''
    db['dms'][dm_id]['messages'].append(message_id)
    telemetry_messages(db, 1)

def message_react_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, 
    add a "react" to that particular message.

    Arguments:
        token (string)      - the token of the user
        message_id (int)    - the id of the message
        react_id (int)      - the id of a react

    Exception:
        InputError  - Occurs when message_id is not a valid message within a 
                        channel or DM that the authorised user has joined.
                                        AND
                    - Occurs when react_id is not a valid react ID - currently,
                        the only valid react ID the frontend has is 1.
                                        AND
                    - Occurs when the message already contains a react with 
                        ID react_id from the authorised user.
    Return Value:
        {}
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    handle = db['users'][auth_user_id]['handle_str']
    if react_id not in VALID_REACT_ID:
        raise InputError("Invalid react_id")

    for channel_id in db['channels']:
        if auth_user_id in db['channels'][channel_id]['members']:
            if message_id in db['channels'][channel_id]['messages']:
                react = db['messages'][message_id]['reacts']
                # Add the notifications 
                u_id = db['messages'][message_id]['u_id']
                channel_name = db['channels'][channel_id]['name']
                notification_message = f"{handle} reacted to your message in {channel_name}"
                db['notifications'][u_id].insert(0,{
                'channel_id': channel_id,
                'dm_id': '-1',
                'notification_message': notification_message
                })
                add_react(react, react_id, auth_user_id)
                return {}

    for dm_id in db['dms']:
        if auth_user_id in db['dms'][dm_id]['members']:
            if message_id in db['dms'][dm_id]['messages']:
                reacts = db['messages'][message_id]['reacts']
                # Add the notifications
                u_id = db['messages'][message_id]['u_id']
                dm_name = db['dms'][dm_id]['name']
                notification_message = f"{handle} reacted to your message in {dm_name}"
                db['notifications'][u_id].insert(0,{
                'channel_id': '-1',
                'dm_id': dm_id,
                'notification_message': notification_message
                })
                add_react(reacts, react_id, auth_user_id)
                return {}

    # at this point message_id is not in any channel/dm message lists i.e invalid
    raise InputError("Message id invalid")

def message_unreact_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, 
    remove a "react" to that particular message.

    Arguments:
        token (string)      - the token of the user
        message_id (int)    - the id of the message
        react_id (int)      - the id of a react

    Exception:
        InputError  - Occurs when message_id is not a valid message within a 
                        channel or DM that the authorised user has joined.
                                        AND
                    - Occurs when react_id is not a valid react ID.
                                        AND
                    - Occurs when the message does not contain a react with 
                        ID react_id from the authorised user
    Return Value:
        {}
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    if react_id not in VALID_REACT_ID:
        raise InputError("Invalid react_id")
    
    for channel_id in db['channels']:
        if auth_user_id in db['channels'][channel_id]['members']:
            if message_id in db['channels'][channel_id]['messages']:
                react = db['messages'][message_id]['reacts']
                remove_react(react, react_id, auth_user_id)
                return {}

    for dm_id in db['dms']:
        if auth_user_id in db['dms'][dm_id]['members']:
            if message_id in db['dms'][dm_id]['messages']:
                reacts = db['messages'][message_id]['reacts']
                remove_react(reacts, react_id, auth_user_id)
                return {}

    # at this point message_id is not in any channel/dm message lists i.e invalid
    raise InputError("Message id invalid")

def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned".

    Arguments:
        token (string)      - the token of the user
        message_id (int)    - the id of the message

    Exception:
        InputError  - Occurs when message_id is not a valid message within a 
                        channel or DM that the authorised user has joined.
                                        AND
                    - Occurs when the message is already pinned.

        AccessError - Occurs when message_id refers to a valid message in a 
                        joined channel/DM and the authorised user does not 
                        have owner permissions in the channel/DM
    Return Value:
        {}
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)

    for channel_id in db['channels']:
        if auth_user_id in db['channels'][channel_id]['members']:
            if message_id in db['channels'][channel_id]['messages']:
                if auth_user_id not in db['channels'][channel_id]['owners']:
                    raise AccessError("The authorised user does not have owner permissions in the channel")
                message_to_pin = db['messages'][message_id]
                pin_message(message_to_pin)
                return {}

    for dm_id in db['dms']:
        if auth_user_id in db['dms'][dm_id]['members']:
            if message_id in db['dms'][dm_id]['messages']:
                if auth_user_id != db['dms'][dm_id]['creator_id']:
                    raise AccessError("The authorised user does not have owner permissions in the DM")
                message_to_pin = db['messages'][message_id]
                pin_message(message_to_pin)
                return {}

    # at this point message_id is not in any channel/dm message lists i.e invalid
    raise InputError("Message id invalid")

def message_unpin_v1(token, message_id):
    '''
    Given a message within a channel or DM, remove its mark as pinned.

    Arguments:
        token (string)      - the token of the user
        message_id (int)    - the id of the message

    Exception:
        InputError  - Occurs when message_id is not a valid message within a 
                        channel or DM that the authorised user has joined.
                                        AND
                    - Occurs when the message is not already pinned.

        AccessError - Occurs when message_id refers to a valid message in a 
                        joined channel/DM and the authorised user does not have 
                        owner permissions in the channel/DM.
    Return Value:
        {}
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)

    for channel_id in db['channels']:
        if auth_user_id in db['channels'][channel_id]['members']:
            if message_id in db['channels'][channel_id]['messages']:
                if auth_user_id not in db['channels'][channel_id]['owners']:
                    raise AccessError("The authorised user does not have owner permissions in the channel")
                message_to_unpin = db['messages'][message_id]
                unpin_message(message_to_unpin)
                return {}

    for dm_id in db['dms']:
        if auth_user_id in db['dms'][dm_id]['members']:
            if message_id in db['dms'][dm_id]['messages']:
                if auth_user_id != db['dms'][dm_id]['creator_id']:
                    raise AccessError("The authorised user does not have owner permissions in the DM")
                message_to_unpin = db['messages'][message_id]
                unpin_message(message_to_unpin)
                return {}

    # at this point message_id is not in any channel/dm message lists i.e invalid
    raise InputError("Message id invalid")

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """
    Share the given original message with message_id og_message_id to a channel or dm
    Arguments:
        token (string)          - the token of the user
        og_message_id (int)     - the id of the original message
        message(string)         - the extra message
        channel_id(int)         - the id of channel to share
        dm_id(int)              - the id of dm to share
    Exception:
        InputError  - Occurs when both channel_id and dm_id are invalid or,
                            neither channel_id nor dm_id are -1 or,
                            og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined or,
                            length of message is more than 1000 characters.

        AccessError - Occurs when the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) 
                            and the authorised user has not joined the channel or DM they are trying to share the message to

    Return Value: {
        'shared_message_id': int,
    }
    """

    if len(message) > 1000:
        raise InputError("Message cannot be longer than 1000 characters")
    
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)

    if channel_id not in db['channels'] and dm_id not in db['dms']:
        raise InputError("Both channel_id and dm_id are Invalid")
    elif channel_id != -1 and dm_id != -1:
        raise InputError("Neither channel_id nor dm_id is -1")

    if og_message_id not in db['messages']:
        raise InputError("Invalid og_message_id")

    og_message = db['messages'][og_message_id]['message']
    new_message = og_message + message

    check_if_user_can_share(og_message_id, db, u_id)

    shared_message_id = None
    if channel_id != -1 and dm_id == -1:
        # share message to a channel
        if u_id not in db['channels'][channel_id]['members']:
            raise AccessError("User is not joined the channel they want to share to")
        shared_message_id = message_send_v1(token, channel_id, new_message)['message_id']
    # elif channel_id == -1 and dm_id != -1:
    else:
        # share message to a dm
        if u_id not in db['dms'][dm_id]['members']:
            raise AccessError("Use is not joined the dm they want to share to")
        shared_message_id = senddm(token, dm_id, new_message)['message_id']

    return {
        'shared_message_id': shared_message_id
    }

def check_if_user_can_share(og_messge_id, db, u_id):

    for channel_info in db['channels'].values():
        
        if og_messge_id in channel_info['messages']:
            
            if u_id not in channel_info['members']:
                raise InputError("user not joined the channel")

    for dm_info in db['dms'].values():
        if og_messge_id in dm_info['messages']:
            if u_id not in dm_info['members']:
                raise InputError("user not joined the dm") 
    return
# Helper functions for message: react; unreact; pin and unpin functions
def add_react(react, react_id, auth_user_id):
    '''
    Adds a react to a message
    '''
    for reaction in react:
        if react_id == reaction['react_id']:
            if auth_user_id in reaction['u_ids']:
                raise InputError("Already reacted by the user")
            reaction['u_ids'].append(auth_user_id)
            return
    react.append({'react_id': react_id, 
                    'u_ids': [auth_user_id]})

def remove_react(react, react_id, auth_user_id):
    '''
    Removes a react from a message
    '''
    for reaction in react:
        if react_id == reaction['react_id']:
            if auth_user_id not in reaction['u_ids']:
                raise InputError("Does not contain this reaction from authorised user")
            reaction['u_ids'].remove(auth_user_id)
            return
    return

def pin_message(message):
    '''
    pin a given message
    '''
    if message['is_pinned'] == False:
        message['is_pinned'] = True
        return
    else:
        raise InputError("The message is already pinned")

def unpin_message(message):
    '''
    unpin a given message
    '''
    if message['is_pinned'] == True:
        message['is_pinned'] = False
        return
    else:
       raise InputError("The message is not already pinned")


def telemetry_messages(db, delta: int):
    messages_exist = db['workspace_stats']['messages_exist']
    num_messages_exist = messages_exist[-1]['num_messages_exist']
    messages_exist.append({
        'num_messages_exist': num_messages_exist + delta,
        'time_stamp': int(time.time()),
    })

