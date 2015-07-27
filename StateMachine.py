# -*- coding: utf-8 -*-
from enum import Enum


class States(Enum):
    """
    A simple state machine to easier navigation through @decorator functions
    in alarms_bot.py
    """
    STATE_START = 0
    STATE_NEWALARM = 1
    STATE_SETTING_TIMEZONE_SEPARATE = 2
    STATE_SETTING_TIMEZONE_FOR_ALARM = 3
    STATE_SETTING_TIME = 4
    STATE_SETTING_TEXT = 5