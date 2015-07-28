#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
"""
This script is triggered by "at" command (man at for more)
Even if bot has stopped, this script will run, because data is saved
in "atjobs" folder somewhere in system
"""
import telebot
import sys
from config import token
bot = telebot.TeleBot(token)
bot.send_message(int(sys.argv[1]), (sys.argv[2]))
