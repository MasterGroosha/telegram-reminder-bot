# -*- coding: utf-8 -*-

token = 'TOKEN'

log_name = 'alarms_bot'
log_level = 'debug'

# Values for "in the morning", "at noon" (twice because of russian E/Ё letters),
# "in the evening", "at night"
values_lexical = ['утром', 'днём', 'днем', 'вечером', 'ночью']

# Server's offset from UTC
# А надо ли?
server_offset = 3

database_offsets_file = 'users_offsets'
database_schedules_file = 'schedules.db'
