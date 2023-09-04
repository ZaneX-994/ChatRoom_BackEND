import re
import secrets
import jwt
import hashlib
from jwt import InvalidSignatureError, DecodeError
from src.data_store import data_store
from src.error import InputError, AccessError
from src.config import SECRET


VALID_EMAIL_PATTERN = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
NON_ALPHANUMERIC = re.compile(r'[^a-z0-9]')

PERMISSIONS_OWNER = 1
PERMISSIONS_MEMBER = 2


def auth_login_v1(email, password):
    """
    Attempts to login an existing user.

    Arguments:
        email (string)      - The email of the user
        password (string)   - The password the user has provided

    Exceptions:
        InputError  - Occurs when the email or password is invalid

    Return Value:
        Returns { auth_user_id, token } when successful where auth_user_id
        is the user ID for the logged in user and the session token
    """
    db = data_store.get()
    if email not in db['emails']:
        raise InputError("Email does not exist")

    # Check password hash matches.
    user = db['emails'][email]
    if hash_password(user['u_id'], password) != user['hash']:
        raise InputError("Password is incorrect")

    return {
        'token': generate_token(db, user['u_id']),
        'auth_user_id': user['u_id'],
    }


def auth_register_v1(email, password, name_first, name_last):
    """
    Attempts to register a new user.

    Arguments:
        email (string)      - The email of the user
        password (string)   - The password the user has provided
        name_first (string) - The first name of the user
        name_last (string)  - The last name of the user

    Exceptions:
        InputError  - Occurs when the email, password, first name, or last name
                    is invalid

    Return Value:
        Returns { auth_user_id, token } when successful where auth_user_id
        is the user ID for the newly registered user and the session token
    """
    db = data_store.get()
    # Validate the email.
    if VALID_EMAIL_PATTERN.search(email) is None:
        raise InputError("Invalid email")
    if email in db['emails']:
        raise InputError("Email already exists")

    # Validate password length.
    if len(password) < 6:
        raise InputError("Password is too short")

    # Validate name lengths.
    if not (1 <= len(name_first) <= 50):
        raise InputError("First name must be between 1 and 50 characters inclusive")
    if not (1 <= len(name_last) <= 50):
        raise InputError("Last name must be between 1 and 50 characters inclusive")

    u_id = len(db['users'])
    handle_str = generate_handle(db['handles'], name_first, name_last)
    db['handles'][handle_str] = u_id

    db['emails'][email] = {
        'u_id': u_id,
        'hash': hash_password(u_id, password),
    }

    # Assign global permissions.
    if not db['users']:
        # No other users registered.
        permission_id = PERMISSIONS_OWNER
    else:
        permission_id = PERMISSIONS_MEMBER
    db['global_permissions'][u_id] = permission_id

    # Store the notifications 
    db['notifications'][u_id] = []

    db['users'][u_id] = {
        'u_id': u_id,
        'email': email,
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle_str,
    }
    # add reset code to the user
    db['reset_code'][u_id] = generate_reset_code()
    
    db['sessions_list'][u_id] = [] 
    return {
        'token': generate_token(db, u_id),
        'auth_user_id': u_id,
    }

def auth_logout_v1(token):
    """
    Attempts to logout the user
    Arguments:
        token (string)      - The token of the user
    Exceptions:
        AccessError  - Occurs when the user is already loged out and token
                    is invalid

    """
    
    db = data_store.get()

    u_id = extract_validate_token_user_id(db, token)

    session_id = jwt.decode(token, SECRET, algorithms=['HS256'])['session_id']
    
    db['sessions_list'][u_id].remove(session_id) 
    
    return {}

def auth_passwordreset_request_v1(email):
    """
    Attempts to send passwordreset request

    Arguments:
        email (string)      - The email of the user
    """
    db = data_store.get()

    if email in db['emails']:
        # if the email belongs a valid user, return the unique reset code to server
        # and remove this code with a new one
        u_id = db['emails'][email]['u_id']

        # log user out of every sessions
        db['sessions_list'][u_id] = []
        
        return db['reset_code'][u_id]
    
    return {}

def auth_passwordreset_reset_v1(reset_code, new_password):
    """
    Attempts to reset password

    Arguments:
        reset_code (string)      - The specific reset code of the user
        new_password (string)    - The password user wanna reset to
    
    Exceptions:
        InputError          - Occurs when reset_code is not valid or new_password is shorter than 6
    """
    # Error check
    if len(new_password) < 6:
        raise InputError("New password should be at least 6 characters!")
    
    db = data_store.get()

    if reset_code not in db['reset_code'].values():
        raise InputError("This Reset_Code is Not Valid")
    
    # change password
    u_id = list(filter(lambda u_id: db['reset_code'][u_id] == reset_code, db['reset_code']))[0]
    email = db['users'][u_id]['email']
    db['emails'][email]['hash'] = hash_password(u_id, new_password)
    return {}

def generate_reset_code():
    return secrets.token_hex(16)

def hash_password(u_id, password):
    """
    Cryptographically hashes a password with a salt and pepper.
    """
    pepper = SECRET
    salt = str(u_id)
    s = (password + salt + pepper).encode('utf-8')
    return hashlib.sha1(s).hexdigest()


def generate_handle(existing_handles, name_first, name_last):
    """
    Generates the handle for a new user.

    Arguments:
        existing_handles (dictionary)   - The handles already used
        name_first (string)             - The first name of the user
        name_last (string)              - THe last name of the user

    Return Value:
        Returns the new handle (string) for the user
    """
    handle_str = (name_first + name_last).lower()
    handle_str = re.sub(NON_ALPHANUMERIC, '', handle_str)
    handle_str = handle_str[:20]

    if handle_str not in existing_handles:
        return handle_str

    # Discriminant needs to be appended to handle.
    discriminant = 0
    while (handle_str + str(discriminant)) in existing_handles:
        discriminant += 1
    return handle_str + str(discriminant)


def generate_token(db, auth_user_id):
    """
    Generates a token from the session_id pool and a auth_user_id
    """
    session_id = db['next_session_id']
    db['sessions_list'][auth_user_id].append(session_id)
    token = construct_token(session_id, auth_user_id)
    db['next_session_id'] += 1
    return token


def construct_token(session_id, auth_user_id):
    """
    Constructs a signed JWT token with the session_id and auth_user_id
    """
    payload = {
        'session_id': session_id,
        'u_id': auth_user_id,
    }

    return jwt.encode(payload, SECRET, algorithm="HS256")    


def extract_validate_token_user_id(db, token):
    '''
    Aims to check if the token is valid and extracts the user id.

    Arguments:
        token(str)              - the token of the creator
        db(dictionary)          - data

    Exception:
        AccessError - Occurs when the token is not valid (e.g. the user is not registered before)

    Return Value:
        Returns the user id from the decrypted token.
    '''
    try:
        data = jwt.decode(token, SECRET, algorithms=['HS256'])
        assert data['u_id'] in db['users']
    except (InvalidSignatureError, DecodeError) as error:
        raise AccessError('Invalid token') from error

    if is_user_deleted(db, data['u_id']):
        raise AccessError('User has been deleted')
    if data['session_id'] not in db['sessions_list'][data['u_id']]:
        raise AccessError('Invalid session_id in token')
    return data['u_id']


def is_user_deleted(db, u_id) -> bool:
    return u_id not in db['global_permissions']

