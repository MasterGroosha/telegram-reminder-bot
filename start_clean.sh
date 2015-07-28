#!/bin/sh
export LC_ALL=en_US.UTF-8
rm *.db
rm alarms_bot.log
./init_database.py
./alarms_bot.py
