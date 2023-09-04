from src.data_store import data_store
from src.error import InputError
from src.auth import extract_validate_token_user_id

def search_v1(token, query_str):
    """
    Given a query string, return a collection of messages in all of the channels/
    DMs that the user has joined that contain the query (case-insensitive).
    There is no expected order for these messages.

    Arguments:
        token (str) - A registered user's token
        query_str (str) - The pattern that the user wants to find in the message collection

    Exceptions:
        InputError - When length of query_str is less than 1 OR over 1000 characters
        AccessError - Thrown when the token passed in is invalid.

    Return Value:
        Returns { messages } given a valid token str is inputted.
        messages will be a list of dictionaries >> [{},{},{}],
        where each dictionary contains types { message_id, u_id, message, time_sent, reacts, is_pinned }
        
    """
    db = data_store.get()
    user = extract_validate_token_user_id(db, token)

    # Check that the query string is an acceptable length
    if len(query_str) < 1:
        raise InputError("query_str needs to be at least 1 character long")
    if len(query_str) > 1000:
        raise InputError("query_str can only be at most be 1000 characters long")

    msg_ids_to_be_examined = []
    channels = db['channels']
    for _, channel in channels.items():
        if user in channel['members']:
            msg_ids_to_be_examined += channel['messages']
    dms = db['dms']
    for _, dm in dms.items():
        if user in dm['members']:
            msg_ids_to_be_examined += dm['messages']
    
    
    pattern_occurences = []
    messages = db['messages']
    for m_id, msg in messages.items():
        if m_id in msg_ids_to_be_examined and query_str.lower() in msg['message'].lower():
            pattern_occurences.append(msg)

    return {'messages': pattern_occurences}