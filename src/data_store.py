import time

'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''



def create_default_db():
    creation_time = int(time.time())
    return {
        # users[u_id] = {
        #   u_id: number,
        #   email: string,
        #   name_first: string,
        #   name_last: string,
        #   handle_str: string,
        # }
        'users': {},
        # reset_code['reset_code'] = u_id
        'reset_code':{},
        # global_permissions[u_id] = permission_id: integer
        # Removed users will not have a key present in the
        # 'global_permissions' dictionary for their user id.
        'global_permissions': {},
        # emails[email] = { 
        #   u_id: number, 
        #   hash: string, (the hash of the user's password)
        # }
        'emails': {},
        # handles[handle_str] = u_id: number
        'handles': {},
        # channels[channel_id] = {
        #   'name': name,
        #   'ispublic': is_public,
        #   'messages': [message_ids],
        #   'members': [],
        #   'owners': [],
        #   'standup_info':{
        #     'is_active': False,
        #     'starter': u_id(int),
        #     'time_finish': time_finish(int),
        #     'buffer': [{'message_sender1_handle': message1}]
        # }
        'channels': {},
        # dms[dm_id] = {
        # 'name': string,
        # 'creator_id': number, (the original DM creator)
        # 'members': [], (list of all user ids in this dm)
        # 'messages': [message_ids], (list of message_ids)
        # }
        'dms': {},
        # message[message_id] = {
        #  'message_id': number,
        #  'u_id': number,
        #  'message': string,
        #  'time_sent': number,
        #  'reacts': [{react_id: 1,
        #             u_ids: ...}]
        #  'is_pinned': BOOLEAN (TRUE/FALSE)
        # }
        'messages': {},
        # sessions_list = dict of list of session_ids
        # sessins_list[u_id] = []
        'sessions_list': {},
        # integer
        'next_session_id': 0, 
        # notifications[u_id]= [{
        #     'channel_id': number,
        #     'dm_id': number,
        #     'notification_message': string},
        # ] (list of notifications dict )
        'notifications': {},
        'workspace_stats': {
            # [{num_channels_exist, time_stamp}]
            'channels_exist': [{ 'num_channels_exist': 0, 'time_stamp': creation_time}],
            # [{num_dms_exist, time_stamp}]
            'dms_exist': [{ 'num_dms_exist': 0, 'time_stamp': creation_time}],
            # [{num_messages_exist, time_stamp}]
            'messages_exist': [{ 'num_messages_exist': 0, 'time_stamp': creation_time}],
        },
    }

class Datastore:
    def __init__(self):
        self.__store = create_default_db()

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()
