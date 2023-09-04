from src.data_store import data_store
from src.error import AccessError
from src.auth import extract_validate_token_user_id, is_user_deleted

def users_all_v1(token):
    """
    Returns a list of all users and their associated details.

    Arguments:
        token (str) - A registered user's token

    Exceptions:
        AccessError - Thrown when the token passed in is invalid.

    Return Value:
        Returns { users } given a valid token str is inputted.
        users will be a list of dictionaries >> [{},{},{}]
        Each of these dictionaries will represent a user, containing its
        u_id(int), email(str), name_first(str), name_last(str), handle_str(str)
        
    """
    db = data_store.get()
    extract_validate_token_user_id(db, token)
    return {
        'users': [user for u_id, user in db['users'].items() if u_id in db['global_permissions']],
    }


def users_stats(token):
    """
    Returns the workspace stats analytics.

    Arguments:
        token (str) - A registered user's token

    Return Value:
        Returns { workspace_stats } where `workspace_stats` takes the form:
        { channels_exist, dms_exist, messages_exist, utilization_rate }
        
    """
    db = data_store.get()
    extract_validate_token_user_id(db, token)

    # Calculate utilization.
    num_active_users = 0
    num_users = 0
    for u_id in db['users']:
        if is_user_deleted(db, u_id):
            continue

        # Check user activity.
        is_active = False
        for ch in db['channels'].values():
            if u_id in ch['members']:
                is_active = True
        for dm in db['dms'].values():
            if u_id in dm['members']:
                is_active = True

        if is_active:
            num_active_users += 1
        num_users += 1

    stats = db['workspace_stats'].copy()
    stats['utilization_rate'] = num_active_users / num_users
    return {
        'workspace_stats': stats,
    }
