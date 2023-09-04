- u_ids and channel_id (i.e. the integer value in {'auth_user_id': <some_integer>, 'channel_id': <some_integer>}) are non-negative.
- when being registered into the data_store, a new user will be assigned a u_id equal to the current number of users stored in the data_store, (so does the channel_id)
- The values provided as arguments to the external facing functions have the types as denoted in the specification
- For the variable is_public in channels, we assume true means it is public and false means not public
- Assume 'owners' in each channel is a subset of 'members'
- DMS can have just the creator in them
- Removed users can still be added to channels and dms

