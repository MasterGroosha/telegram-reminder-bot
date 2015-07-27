#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import telebot
import sys
from config import token
file = open('log.log', 'w+t')
file.write('Sender started')
file.close()
bot = telebot.TeleBot(token)
msg = bytes(sys.argv[2],'utf-8').decode('utf-8')
bot.send_message(int(sys.argv[1]), sys.argv[2])
# .replace('\"','\\"')