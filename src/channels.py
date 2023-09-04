import time

from src.data_store import data_store
from src.error import InputError
from src.auth import extract_validate_token_user_id


def channels_list_v1(token):
    '''
    Aim to list the infomation of channels where auth_user is a member of
    Arguments:
        token(str)       - contains the detail of the user

    Exception:
        AccessError      - Occurs when the token is not valid
        (i.e., the user is not registered before)

    Return Value:
        Returns { channels } when successful where channels is a list of dictionaries
        that contains type {channel_id, name}
    '''
    db = data_store.get()

    # check if auth_user_id is valid
    auth_user_id = extract_validate_token_user_id(db, token)
    channels = []
    # search for members
    for channel_id, channel in db['channels'].items():
        if auth_user_id in channel['members']:
            channels.append({
                'channel_id': channel_id,
                'name': channel['name'],
            })

    return {
        'channels': channels
    }

def channels_listall_v1(token):
    """
    Provides a list of all channels, including private channels, (and their associated details).

    Arguments:
        token (str) - The user's token

    Exceptions:
        AccessError - Thrown when the token passed in is invalid.

    Return Value:
        Returns { channels } given a valid token str is inputted.
        channels will be a list of dictionaries >> [{},{},{}] 
        Each of these dictionaries will represent a channel, showing its id number
        in the data_store as well as its name, e.g.
        {"channel_id": 0, "name": "Funny Cats",}
        
    """
    # if type(token) is not str:
    #     raise AccessError("Invalid token")

    db = data_store.get()
    extract_validate_token_user_id(db, token)
    
    # The following will be a LIST of dictionaries with 'channel_id' & 'name' entries 
    channel_data_list = []
    for c_id, channel in db['channels'].items():
        id_name_pair =  {
            'channel_id': c_id, 
            'name': channel['name'],
        }
        channel_data_list.append(id_name_pair)
    
    return {
        'channels': channel_data_list,
    }


def channels_create_v1(token, name, is_public):
    '''
    Aim to create a new channel where the creator is a member of

    Arguments:
        token(string)           - contains the detail of the creator
        name(string)            - the name of the channel
        is_public(boolean)      - the property of the channel

    Exception:
        InputError  - Occurs when the length of the name of channel is
        less than 1 or more than 20 characters

        AccessError - Occurs when the token is not valid
        (i.e., the user is not registered before)

    Return Value:
        Returns { channels } if the channel is created successfully
        channels is a list of dictionary that contains {channel_id, name}
    '''
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)

    # Check if the name is valid
    if not 1 <= len(name) <= 20:
        raise InputError('Invalid name for channels')
    
    channel_id = len(db['channels'])

    db['channels'][channel_id] = {
        'name': name,
        'ispublic': is_public,
        'messages': [],
        'members': [auth_user_id],
        'owners': [auth_user_id],
        'standup_info': {
            'is_active': False,
            'starter': None,
            'time_finish': None,
            'buffer': [],
        }
    }

    telemetry_channels(db, 1)
    return {
        'channel_id': channel_id,
    }


def telemetry_channels(db, delta: int):
    channels_exist = db['workspace_stats']['channels_exist']
    num_channels_exist = channels_exist[-1]['num_channels_exist']
    channels_exist.append({
        'num_channels_exist': num_channels_exist + delta,
        'time_stamp': int(time.time()),
    })

