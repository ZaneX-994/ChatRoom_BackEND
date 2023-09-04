import sys
import signal
import json
import os

from json import dumps
from flask import Flask, request, send_file
from flask_mail import Mail, Message
from flask_cors import CORS
from src import config
from src.data_store import data_store
from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1, channel_messages_v1, channel_removeowner_v1, channel_leave_v1, channel_addowner_v1
from src.message import message_edit_v1, message_remove_v1, message_send_v1, message_react_v1, message_unreact_v1
from src.message import message_pin_v1, message_unpin_v1, message_share_v1, message_sendlater_v1, message_sendlaterdm_v1
from src.dm import dm_create, senddm, dm_messages, dm_remove, dm_leave, dm_details, dm_list_v1
from src.user import user_profile, profile_sethandle, user_profile_setemail, set_name, profile_uploadphoto, image_file_path
from src.admin import user_remove, userpermission_change_v1
from src.users import users_all_v1, users_stats
from src.notifications import notifications_get_v1
from src.search import search_v1
from src.standup import standup_start_v1, standup_send_v1, standup_active_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'msgsend1@gmail.com'
APP.config['MAIL_PASSWORD'] = 'asimplepassword'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail= Mail(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

PERSISTENT_DB_FILE = "data.db"

# Load data from file.
try:
    f = open(PERSISTENT_DB_FILE, "r")
    db = json.load(f)
    data_store.set(db)
except IOError:
    print("No database loaded")

# Save json to file.
def save_data(response):
    db = data_store.get()
    with open(PERSISTENT_DB_FILE, "w") as f:
        json.dump(db, f)
    return response

# Save data after every request.
APP.after_request(save_data)

# Clear (i.e. reset the data_store)
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    """
    Resets the data store to a blank state.
    """
    clear_v1()
    return dumps({})

# AUTH ROUTES
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login():
    """
    Logins a user.
    """
    return dumps(auth_login_v1(
        request.json['email'],
        request.json['password'],
    ))

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    """
    Registers a user.
    """
    return dumps(auth_register_v1(
        request.json['email'],
        request.json['password'],
        request.json['name_first'],
        request.json['name_last'],
    ))

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    """
    Logout a user
    """
    auth_logout_v1(request.json['token'])
    return dumps({})

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_passwordreset_request():
    email = request.json['email']
    reset_code = auth_passwordreset_request_v1(email)

    if reset_code != {}:
        msg = Message('reset code', sender = 'msgsend1@gmail.com', recipients = [email])
        msg.body = reset_code
        mail.send(msg)
    return dumps({})

@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])
def auth_passwordreset_reset():
    print(request.json['new_password'])
    return dumps(auth_passwordreset_reset_v1(
        request.json['reset_code'],
        request.json['new_password'],
    ))


# CHANNELS ROUTES
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    '''
    Create a channel
    '''
    return dumps(channels_create_v1(
        request.json['token'],
        request.json['name'],
        request.json['is_public'],
    ))

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    '''
    List all channels for a user
    '''
    return dumps(channels_list_v1(request.args.get('token')))

@APP.route("/channels/listall/v2", methods=['GET'])
def list_channels():
    """
    Provides a list of all channels, including private channels, (and their associated details).
    """
    token = request.args.get('token')
    return(dumps(channels_listall_v1(token)))

# CHANNEL ROUTES
@APP.route("/channel/invite/v2", methods = ['POST'])
def channel_invite():
    """
    Invites a user to a channel
    """
    data = request.get_json()
    chnl_token = data['token']
    chnl_id = data['channel_id']
    chnl_uid = data['u_id']
    channel_invite_v1(chnl_token, chnl_id, chnl_uid)
    return dumps({})

@APP.route("/channel/details/v2", methods = ['GET'])
def channel_dets():
    """
    Returns basic details of a channel the authorised user is a member.
    """
    chnl_token = request.args.get('token')
    chnl_id = int(request.args.get('channel_id'))
    return dumps(channel_details_v1(chnl_token, chnl_id))

@APP.route("/channel/join/v2", methods=['POST'])
def join_channel():
    """
    Given a channel_id of a channel that the authorised user's
    token can join, adds them to that channel.

    Returns:
        json str: An empty dictionary (jsonified)
    """
    return dumps(channel_join_v1(
        request.json['token'], request.json['channel_id']
    ))
    
@APP.route("/channel/leave/v2", methods=['POST'])
def leave_channel():
    """
    Given a channel with ID channel_id that the authorised user is a
    member of, remove them as a member of the channel. Their messages
    should remain in the channel. If the only channel owner leaves,
    the channel will remain.

    Returns:
        json str: An empty dictionary (jsonified)
    """
    return dumps(channel_leave_v1(
        request.json['token'], request.json['channel_id']
    ))

@APP.route("/channel/addowner/v2", methods=['POST'])
def add_channel_owner():
    """
    Make user with user id u_id an owner of the channel.

    Returns:
        json str: An empty dictionary (jsonified)
    """
    return dumps(channel_addowner_v1(
        request.json['token'],
        request.json['channel_id'],
        request.json['u_id']
    ))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    """
    Remove the user as owner of the channel
    """
    channel_removeowner_v1(
        request.json['token'],
        request.json['channel_id'],
        request.json['u_id'])
    return dumps({})

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    """
    Check the messages in channel
    """
    return dumps(channel_messages_v1(
        request.args.get('token'),
        int(request.args.get('channel_id')),
        int(request.args.get('start')),
    ))

# MESSAGE ROUTES
@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    """
    Seed the messages in the channel
    """
    requests = request.get_json()
    token = requests['token']
    channel_id = requests['channel_id']
    message = requests['message']
    return_message_id = message_send_v1(token, channel_id, message)
    return dumps(return_message_id)

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    """
    Edit the message in channel/dm
    """
    requests = request.get_json()
    token = requests['token']
    message_id = requests['message_id']
    message = requests['message']
    return_info = message_edit_v1(token, message_id, message)
    return dumps(return_info)

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    """
    Remove the message in the channel/dm
    """
    return dumps(message_remove_v1(
        request.json['token'],
        request.json['message_id'],
    ))

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    """
    Seed the messages in the channel at a specified time in the future.
    """
    requests = request.get_json()
    token = requests['token']
    channel_id = requests['channel_id']
    message = requests['message']
    time_sent = requests['time_sent']
    return_message_id = message_sendlater_v1(token, channel_id, message, time_sent)
    return dumps(return_message_id)

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm():
    """
    Seed the messages in the dm at a specified time in the future.
    """
    requests = request.get_json()
    token = requests['token']
    dm_id = requests['dm_id']
    message = requests['message']
    time_sent = requests['time_sent']
    return_message_id = message_sendlaterdm_v1(token, dm_id, message, time_sent)
    return dumps(return_message_id)

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    """
    Adds a 'react' to a particular message.
    """
    data = request.get_json()
    msg_token = data['token']
    msg_msg_id = data['message_id']
    msg_react_id = data['react_id']
    message_react_v1(msg_token, msg_msg_id, msg_react_id)
    return dumps({})

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    """
    Removes a 'react' to a particular message.
    """
    data = request.get_json()
    msg_token = data['token']
    msg_msg_id = data['message_id']
    msg_react_id = data['react_id']
    message_unreact_v1(msg_token, msg_msg_id, msg_react_id)
    return dumps({})

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    """
    Given a message within a channel or DM, mark it as "pinned".
    """
    data = request.get_json()
    msg_token = data['token']
    msg_msg_id = data['message_id']
    message_pin_v1(msg_token, msg_msg_id)
    return dumps({})

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    """
    Given a message within a channel or DM, remove its mark as pinned.
    """
    data = request.get_json()
    msg_token = data['token']
    msg_msg_id = data['message_id']
    message_unpin_v1(msg_token, msg_msg_id)
    return dumps({})

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    """
    share message to a channel or a dm
    """

    return dumps(message_share_v1(
        request.json['token'],
        request.json['og_message_id'],
        request.json['message'],
        request.json['channel_id'],
        request.json['dm_id'],
    ))

# DM ROUTES
@APP.route("/dm/create/v1", methods=['POST'])
def route_dm_create():
    """
    Creates a dm.
    """
    return dumps(dm_create(
        request.json['token'],
        request.json['u_ids'],
    ))

@APP.route("/dm/details/v1", methods=["GET"])
def dm_details_v1():
    """
    Get the detail of the DM that the given user is a member of
    """

    return dumps(dm_details(
        request.args.get('token'),
        int(request.args.get('dm_id')),
    ))

@APP.route("/dm/leave/v1", methods=["POST"])
def dm_leave_v1():
    """
    Leave the given dm
    """
    return dumps(dm_leave(
        request.json['token'],
        request.json['dm_id'],
    ))

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    """
    Sends a message in a DM.
    """
    return dumps(senddm(
        request.json['token'],
        request.json['dm_id'],
        request.json['message'],
    ))


@APP.route("/dm/messages/v1", methods=['GET'])
def route_dm_messages():
    """
    Sends a message in a DM.
    """
    return dumps(dm_messages(
        request.args.get('token'),
        int(request.args.get('dm_id')),
        int(request.args.get('start')),
    ))

@APP.route("/dm/list/v1", methods=['GET'])
def dms_list():
    """
    Returns the list of DMs that the user is a member of.
    """
    return dumps(dm_list_v1(request.args.get('token')))

@APP.route("/dm/remove/v1", methods=["DELETE"])
def dm_remove_v1():
    """
    Remove a DM
    """
    return dumps(dm_remove(
        request.json['token'],
        request.json['dm_id']
    ))

# USERS ROUTES
@APP.route("/users/all/v1", methods=['GET'])
def get_users_list():
    '''
    Returns a list of all users and their associated details.
    '''
    return dumps(users_all_v1(request.args.get('token')))


@APP.route("/users/stats/v1", methods=['GET'])
def get_users_stats():
    '''
    Returns workspace analytics.
    '''
    return dumps(users_stats(
        request.args.get('token'),
    ))


# USER ROUTES
@APP.route("/user/profile/v1", methods=['GET'])
def profile():
    '''
    Get the profile of a user.
    '''
    return dumps(user_profile(
        request.args.get('token'),
        int(request.args.get('u_id')),
    ))

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    """
    Update the authorised user's first and last name
    """
    return dumps(set_name(
        request.json['token'],
        request.json['name_first'],
        request.json['name_last']
    ))

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail_v1():
    """
    Set the email of the given user
    """
    return dumps(user_profile_setemail(
        request.json['token'],
        request.json['email'],
    ))

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def sethandle():
    '''
    Sets the handle of a user profile.
    '''
    return dumps(profile_sethandle(
        request.json['token'],
        request.json['handle_str'],
    ))

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto():
    """
    Sets the profile photo of a user
    """
    return dumps(profile_uploadphoto(
        request.json['token'],
        request.json['img_url'],
        request.json['x_start'],
        request.json['y_start'],
        request.json['x_end'],
        request.json['y_end'],
    ))

@APP.route("/user/profile/images", methods=['GET'])
def user_profile_image():
    u_id = request.args.get("u_id")
    profile_image_path = image_file_path(u_id)
    if os.path.exists(profile_image_path):
        return send_file("../" + profile_image_path)
    else:
        return send_file("../images/default.jpg")


# ADMIN ROUTES
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def route_user_remove():
    '''
    Removes a user.
    '''
    return dumps(user_remove(
        request.json['token'],
        request.json['u_id'],
    ))

@APP.route("/admin/userpermission/change/v1", methods = ['POST'])
def admin_userpermissions_change():
    """
    Sets the user's permissions to new permissions described by permission_id
    """
    return dumps(userpermission_change_v1(
        request.json['token'],
        request.json['u_id'],
        request.json['permission_id']
    ))

# NOTIFICATION ROUTES
@APP.route("/notifications/get/v1", methods = ['get'])
def get_notifications():
    """
    Get the user's most recent 20 notifications 
    """
    return dumps(notifications_get_v1(request.args.get('token')))

# STANDUP ROUTES
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    """
    start the standup period in the given channel
    """
    return dumps(standup_start_v1(
        request.json['token'],
        request.json['channel_id'],
        request.json['length'],
    ))
@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    """
    send message to get buffered in the standup queue
    """
    return dumps(standup_send_v1(
        request.json['token'],
        request.json['channel_id'],
        request.json['message']
    ))

@APP.route("/standup/active/v1", methods=['GET'])
def check_if_standup_active_in_channel():
    '''
    For a given channel, return whether a standup is active in it,
    and what time the standup finishes. 
    If no standup is active, then time_finish returns None.
    '''
    return dumps(standup_active_v1(
        request.args.get('token'),
        int(request.args.get('channel_id'))
    ))

@APP.route("/search/v1", methods=['GET'])
def search():
    return dumps(search_v1(
        request.args.get('token'),
        request.args.get('query_str')
    ))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port




