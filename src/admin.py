
from src.data_store import Datastore, data_store
from src.error import InputError, AccessError
from src.auth import extract_validate_token_user_id, PERMISSIONS_OWNER, PERMISSIONS_MEMBER


def user_remove(token, target_u_id):
    """
    Removes a user and redacts their name and all their messages.

    Arguments:
        token (string)          - The token of the user making the request
        target_u_id (number)    - The id of the user to remove

    Exceptions:
        InputError  - Occurs when the target user id is invalid or
                    when the target user is the only owner
        AccessError - Occurs when the issuing user is not an owner

    Return Value:
        Returns {} when successful.
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)
    
    # Check if valid target user.
    if target_u_id not in db['users']:
        raise InputError("Target user id is invalid")
    if target_u_id not in db['global_permissions']:
        raise InputError("Target user id has already been deleted")

    # Check if authorized.
    if db['global_permissions'][u_id] != PERMISSIONS_OWNER:
        raise AccessError("User is unauthorized")

    # Count number of owners.
    owners_count = 0
    for permission in db['global_permissions'].values():
        if permission == PERMISSIONS_OWNER:
            owners_count += 1

    # Check if removing only owner.
    assert owners_count > 0
    if owners_count == 1 and u_id == target_u_id:
        raise InputError("Cannot remove only global owner")

    # Remove user data.
    user = db['users'][target_u_id]
    del db['global_permissions'][target_u_id]
    del db['emails'][user['email']]
    del db['handles'][user['handle_str']]

    # Redact messages.
    for message in db['messages'].values():
        if message['u_id'] == target_u_id:
            message['message'] = "Removed user"

    # Remove user from channels and dms.
    for channel in db['channels'].values():
        if target_u_id in channel['members']:
            channel['members'].remove(target_u_id)
        if target_u_id in channel['owners']:
            channel['owners'].remove(target_u_id)
    for dm in db['dms'].values():
        if target_u_id in dm['members']:
            dm['members'].remove(target_u_id)

    # Redact names.
    user['name_first'] = "Removed"
    user['name_last'] = "user"
    return {}

def userpermission_change_v1(token, u_id, permission_id):
    """
    Given a user by their user ID, set their permissions 
    to new permissions described by permission_id

    Arguments:
        token (string)          - The token of the user making the request
        u_id (int)              - The id of the user to remove
        permission_id (int)     - permission id describing the new set of permissions of a user
    Exceptions:
        InputError  - Occurs when u_id does not refer to a valid user.
                                        AND
                    - Occurs when u_id refers to a user who is the only 
                        global owner and they are being demoted to a user.
                                        AND
                    - Occurs when permission_id is invalid.
                                        AND
                    - Occurs when the user already has the permissions level of permission_id.
        AccessError  - Occurs when the authorised user is not a global owner
                                    
    Return Value:
        Returns {} when successful.
    """
    db = data_store.get()

    # Verify if the u_id refers to a valid user
    if u_id not in db['users']:
        raise InputError("u_id does not refer to a valid user")

    # Raise InputError when the only global owner is being demoted 
    owners_count = 0
    for permissions in db['global_permissions'].values():
        if permissions == PERMISSIONS_OWNER:
            owners_count += 1
    if owners_count == 1:
        if db['global_permissions'][u_id] == PERMISSIONS_OWNER:
            if permission_id == PERMISSIONS_MEMBER:
                raise InputError("Global owner being demoted")

    # Verify if the permission_id is valid
    valid_permission_id = [1, 2]
    if permission_id not in valid_permission_id:
        raise InputError("permission_id is invalid")
    
    # Verify if the authorised user trying to amend a user's permissions 
    # is even a global owner; if not then raises AccessError
    uid = extract_validate_token_user_id(db, token)
    if db['global_permissions'][uid] == PERMISSIONS_MEMBER:
        raise AccessError("The authorised user is not a global owner")
    
    # Raises InputError if the user already has the permissions level 
    # of permission_id.
    if db['global_permissions'][u_id] == permission_id:
        raise InputError("The user already has the permissions level of permission_id")

    db['global_permissions'][u_id] = permission_id
    return {}

