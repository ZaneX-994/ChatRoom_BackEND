from src.auth import extract_validate_token_user_id
from src.data_store import data_store

def notifications_get_v1(token):
    """
    Returns the list of notifications about the user.

    Arguments:
        token (string)      - The token of the user

    Exceptions: 
        AccessError - Thrown when the token passed in is invalid.

    Return Value:
        Returns { notifications } when successful where notifications is a list
        of dictionaries, where each dictionary contains
        types { channel_id(int), dm_id(int), notification_message(str) }
    """
    db = data_store.get()
    auth_user_id = extract_validate_token_user_id(db, token)
    notifications_list = []
    num = len(db['notifications'][auth_user_id])
    if num >= 20:
        for notification in db['notifications'][auth_user_id][0:20]:
            notifications_list.append(notification)
    else:
        for notification in db['notifications'][auth_user_id]:
            notifications_list.append(notification)

    return {
        'notifications': notifications_list
    }