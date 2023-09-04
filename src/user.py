import re
import requests
from io import BytesIO

from PIL import Image
from src.config import url
from src.data_store import data_store
from src.error import InputError, AccessError
from src.auth import extract_validate_token_user_id, VALID_EMAIL_PATTERN, NON_ALPHANUMERIC


def user_profile(token, target_u_id):
    """
    Gets the user profile for a user.

    Arguments:
        token (string)          - The token of the user making the request
        target_u_id (number)    - The id of the user to get the profile for

    Exceptions:
        InputError  - Occurs when the target user id is invalid

    Return Value:
        Returns { user } when successful where user
        is the user data of the target user.
    """
    db = data_store.get()
    extract_validate_token_user_id(db, token)
    
    if target_u_id not in db['users']:
        raise InputError("Target user id is invalid")

    user = db['users'][target_u_id].copy()
    user['profile_img_url'] = f"{url}user/profile/images?u_id={target_u_id}"
    return {
        'user': user,
    }
    

def set_name(token, name_first, name_last):
    """
    Update the authorised user's first and last name

    Arguments:
        token (string)          - The token of the user making the request.
        name_first (string)     - First name of the authorised user.
        name_last(string)       - Lasst name of the authorised user.

    Exceptions:
        InputError  - Occurs when the length of name_first is not between 1 and 50 characters inclusive.
                                                AND
                    - Occurs when the length of name_last is not between 1 and 50 characters inclusive.

    Return Value:
        {}
    """
    db = data_store.get()
    # Helper function to check if the token is valid; if so then extract the 
    # user id from it.
    uid = extract_validate_token_user_id(db, token)

    if len(name_first) not in range(1,50):
        raise InputError("Length of first name is not in range 1 to 50")
    if len(name_last) not in range (1,50):
        raise InputError("Length of last name is not in range 1 to 50")

    db['users'][uid]['name_first'] = name_first
    db['users'][uid]['name_last'] = name_last
    return {}

def user_profile_setemail(token, email):
    """
    Update the email of the target

    Arguments:
        token (string)          - The token of the user making the request
        email (string)          - The new email of the user want to use

    Exceptions:
        InputError  - Occurs when email entered is not a valid email 
                    - Occurs when email address is already being used by another user
        AccessError - Occurs when token is invalid
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)

    if VALID_EMAIL_PATTERN.search(email) is None:
        raise InputError("Invalid email")
    if email in db['emails']:
        raise InputError("Email already been taken")
    # store info of origin db['emails'][old_email]
    orgin_email = db['users'][u_id]['email']
    temp = db['emails'][orgin_email]
    db['emails'].pop(orgin_email)

    # restore info in db['emails'][email]
    db['emails'][email] = temp
    db['users'][u_id]['email'] = email
    return {}

def profile_sethandle(token, handle_str):
    """
    Sets the handle of a user profile.

    Arguments:
        token (string)          - The token of the user making the request
        handle_str (string)     - The new handle to be set

    Exceptions:
        InputError  - Occurs when the handle is non-alphanumeric 
                        or of the wrong length or already taken

    Return Value:
        Returns {}
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)
    
    # Check length.
    if not (3 <= len(handle_str) <= 20):
        raise InputError("New handle must be between 3 and 20 characters long")

    # Check alphanumeric.
    if re.search(NON_ALPHANUMERIC, handle_str):
        raise InputError("New handle must be alphanumeric")

    # Check duplicate.
    if handle_str in db['handles']:
        raise InputError("New handle is already taken")

    # Set handle.
    user = db['users'][u_id]
    del db['handles'][user['handle_str']]
    db['users'][u_id]['handle_str'] = handle_str
    db['handles'][handle_str] = u_id
    return {}


def profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """
    Sets a user's profile to a uploaded photo.

    Arguments:
        token (string)          - The token of the user making the request
        img_url (string)        - The url of the profile picture
        x_start (int)           - Left part of the crop
        y_start (int)           - Top part of the crop
        x_end (int)             - Right part of the crop
        y_end (int)             - Bottom part of the crop

    Exceptions:
        InputError  - Occurs when the image URL or image is invalid 
                      Occurs when the crop dimensions are invalid

    Return Value:
        Returns {}
    """
    db = data_store.get()
    u_id = extract_validate_token_user_id(db, token)

    # Grab image.
    headers = {'User-Agent': 'UNSWCOMP1531Bot/0.1'}
    image_response = requests.get(img_url, headers=headers)
    if image_response.status_code != 200:
        raise InputError("Invalid image URL") 

    img = Image.open(BytesIO(image_response.content))
    if img.format != 'JPEG':
        raise InputError("Image is not of JPG format")

    width, height = img.size
    if x_end > width or y_end > height:
        raise InputError("Crop dimensions out of bounds")
    if x_end <= x_start or y_end <= y_start:
        raise InputError("Crop dimensions invalid")

    img = img.crop((x_start, y_start, x_end, y_end))
    img.save(image_file_path(u_id))
    return {}


def image_file_path(u_id):
    return f"images/user_{u_id}.jpg"

