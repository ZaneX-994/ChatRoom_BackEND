from src.data_store import data_store
from src.auth import extract_validate_token_user_id
from src.error import InputError, AccessError
from src.message import message_send_v1
import time
from threading import Timer
from src.channel import check_ids_are_registered_in_db

def standup_start_v1(token, channel_id, length):
    '''
    Aims to start a standup

    Arguments:
        token(str)              - the token of the starter
        channel_id(int)         - id of the channel where the standup happens
        length(int)             - number of seconds that the standup lasts
    
    Exception:
        AccessError             - Occurs when channel_id is valid and the authorised user is not a member of the channel

        InputError              - Occurs when channel_id does not refer to a valid channel,       
                                              length is a negative integer,
                                              an active standup is currently running in the channe.
    '''         
    if length < 0:
        raise InputError('length cannot be negative!')

    db = data_store.get()

    u_id = extract_validate_token_user_id(db, token)

    if channel_id not in db['channels']:

        raise InputError('Channel does not exist!')

    elif u_id not in db['channels'][channel_id]['members']:

        raise AccessError('user is not a member!')
    elif db['channels'][channel_id]['standup_info']['is_active'] == True:
        raise InputError("This channel has an active standup running!")

    time_start = int(time.time())
    
    db['channels'][channel_id]['standup_info'] = {
        'is_active': True,
        'starter': u_id,
        'time_finish': time_start + length,
        'buffer': [],
    }

    Timer(length, standup_message_send, (token, channel_id, db)).start()
    
    return {
        'time_finish': time_start + length
    }
 
def standup_send_v1(token, channel_id, message):
    '''
    Aims to send a message during a standup

    Arguments:
        token(str)              - the token of the sender
        channel_id(int)         - id of the channel where the standup happens
        message(str)            - the message to send
    
    Exception:
        AccessError             - Occurs when channel_id is valid and the authorised user is not a member of the channel

        InputError              - Occurs when channel_id does not refer to a valid channel,
                                              length of message is over 1000 characters,
                                              an active standup is not currently running in the channel.        
    '''
    
    if len(message) > 1000:
        raise InputError("Message cannot be longer than 1000 characters!")
    
    db = data_store.get()
    
    if channel_id not in db['channels']:
        raise InputError("Invalid channel_id!")
    elif db['channels'][channel_id]['standup_info']['is_active'] == False:
        raise InputError("Standup is not running!")
    
    u_id = extract_validate_token_user_id(db, token)

    if u_id not in db['channels'][channel_id]['members']:
        
        raise AccessError("User is not a member of the channel!")

    handle = db['users'][u_id]['handle_str']

    db['channels'][channel_id]['standup_info']['buffer'].append({
        handle: message,
    })

    return {}

def standup_message_send(token, channel_id, db):
    '''
    Aims to send the standup message to the channel by the starter

    Arguments:
        token(str)              - the token of the sender
        channel_id(int)         - id of the channel where the standup happens
        db                      - data_store        
    '''
    message_to_send = ""

    for standup_msg in db['channels'][channel_id]['standup_info']['buffer']:
        for key, value in standup_msg.items():
            message_to_send += key + ': ' + value + '\n'

    if message_to_send != "":
        message_send_v1(token, channel_id, message_to_send)

    db['channels'][channel_id]['standup_info'] = {
        'is_active': False,
        'starter': None,
        'time_finish': None,
        'buffer': [],
    }

    return

def standup_active_v1(token, channel_id):
    """
    For a given channel, return whether a standup is active in it, and what time the standup finishes.
    If no standup is active, then time_finish returns None.

    Arguments:
        token (str) - A registered user's token
        channel_id (int) - The channel id of the channel being checked for a standup

    Exceptions:
        InputError:
            - when channel_id does not refer to a valid channel
        AccessError:
            - when channel_id is valid and the authorised user is not a member of the channel;
            - generally thrown when the token passed in is invalid.

    Return Value:
        Returns { is_active, time_finish } given a valid token (str) and channel_id (int) is inputted.
        is_active (boolean) indicates whether a standup is active in the channel denoted by channel_id.
        time_finish (integer; unix timestamp) indicates and what time the channel's standup finishes 
        (if there is no active standup, time_finish is None).
        
    """
    db = data_store.get()
    user_id = check_ids_are_registered_in_db(token, channel_id, db)
    ch = db['channels'][channel_id]
    if user_id not in ch['members']:
        raise AccessError('User is not a member of this channel')
    return {
        'is_active': ch['standup_info']['is_active'],
        'time_finish': ch['standup_info']['time_finish'],
    }
