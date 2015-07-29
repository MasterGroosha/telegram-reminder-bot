# -*- coding: utf-8 -*-

from lang import *  # Do not delete this line!
token = 'TOKEN'

log_name = 'alarms_bot'  # Log file name
log_level = 'debug'  # debug, info, warning, error


# Server offset from GMT (f.ex Moscow is 3)
server_offset = 0

database_offsets_file = 'users_offsets'
database_states_file = 'state_storage'
database_temp_time_storage = 'temp_time_storage'
database_schedules_file = 'schedules.db'

# Language of bot. Look into "lang" folder for more
lang = ru


# So-called "VIP" users' IDs (can have more than 5 notes at once)
# Made this to prevent spamming notes
vip_list = [11111,22222,33333]

# Allows to temporarly discard all messages except yours
# Looks at alarms_bot.py (cmd_closed_mode function)
is_closed = False
