#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import sys
from time import sleep
import signal

import telebot
import config
import utils
import systemtools
import StateMachine
from SQLighter import SQLighter

bot = telebot.TeleBot(config.token)
global offset_storage
global logger
global state_storage


def signal_handler(signal, frame):
    """
    Set KeyboardInterrupt handler to properly close all DBs
    """
    logger.info('Signal catched, closing databases')
    print('Signal catched, closing databases')
    utils.close_storages()
    sys.exit(0)


# A simple wrapper to set state (inside uses my Shelver)
def set_new_state(chat_id, state_name):
    state_storage.save(str(chat_id), state_name, force_save=True)


# If you want bot to respond only to your messages:
# @bot.message_handler(func=lambda message: message.chat.id != 1111) # your ID here
# def cmd_closed_mode(message):
#     bot.send_message(message.chat.id, 'Bot is closed for testing. Go away')

# Start of interaction
@bot.message_handler(commands=['start'])
def command_help(message):
    logger.debug('User {0!s} started new chat with bot'.format(message.from_user.username))
    # I don't know why to use START state, but why not?
    set_new_state(message.chat.id, StateMachine.States.STATE_START)
    bot.send_message(message.chat.id, config.lang.s_common_welcome_text)


# User is going to set alarm
@bot.message_handler(commands=['newalarm'])
def cmd_new_alarm(message):
    mydb = SQLighter(config.database_schedules_file)
    # If not in VIP list - exit
    if mydb.count_entries_for_id(message.chat.id) == 5 and int(message.chat.id) not in config.vip_list:
        bot.send_message(message.chat.id, config.lang.s_error_maximum_number_of_notes)
        mydb.close()
        return None

    set_new_state(message.chat.id, StateMachine.States.STATE_NEWALARM)

    # if user haven't set timezone - ask him to set one
    if not offset_storage.exists(str(message.chat.id)):
        logger.debug('User {0!s} is going to set new alarm. It\'s his first appear'.format(
            message.from_user.username))
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM)
        bot.send_message(message.chat.id, config.lang.s_common_guide_timezone)
    # if we already have his timezone saved - ask him to set time
    else:
        logger.debug('User {0!s} is going to set new alarm. He has been here before'.format(
            message.from_user.username))
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIME)
        bot.send_message(message.chat.id, config.lang.s_common_guide_time)


# Standalone timezone setting. See below for explanation
@bot.message_handler(commands=['setoffset'])
def cmd_set_offset(message):
    logger.debug('User {0!s} is going to set offset'.format(message.from_user.username))
    set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIMEZONE_SEPARATE)
    bot.send_message(message.chat.id, config.lang.s_common_guide_timezone)


# If cancel - reset state
@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    set_new_state(message.chat.id, StateMachine.States.STATE_START)
    logger.debug('User {0!s} cancelled current task'.format(message.from_user.username))
    bot.send_message(message.chat.id, config.lang.s_common_cancel)


# User is setting timezone
'''
A little explanation: my bot will ask user to set timezone on first usage AND user can set timezone himself
whenever he wants. This way I'm making 2 TIMEZONE states instead of one: one will show guide how to set
time and the other one will just confirm updating timezone without other steps
'''
@bot.message_handler(func=lambda message: state_storage.get(str(message.chat.id)) in [StateMachine.States.STATE_SETTING_TIMEZONE_SEPARATE, StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM])
def cmd_update_timezone_for_user(message):
    # Пытаемся распознать его сообщение
    timezone = utils.parse_timezone(message.text)
    if timezone is None:
        # "Could not recognize timezone"
        bot.send_message(message.chat.id, config.lang.s_error_timezone_not_recognized)
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM)
        return None
    else:
        logger.debug('User {1!s} set timezone: {0!s}'.format(timezone, message.from_user.username))
        offset_storage.save(key=str(message.chat.id), value=timezone, force_save=True)
        if state_storage.get(str(message.chat.id)) == StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM:
            bot.send_message(message.chat.id, config.lang.s_common_guide_time)
            set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIME)
        if state_storage.get(str(message.chat.id)) == StateMachine.States.STATE_SETTING_TIMEZONE_SEPARATE:
            # "Timezone saved. Thank you!"
            bot.send_message(message.chat.id, config.lang.s_common_timezone_set)
            set_new_state(message.chat.id, StateMachine.States.STATE_START)


# User is setting time
@bot.message_handler(func=lambda message: state_storage.get(
    str(message.chat.id)) == StateMachine.States.STATE_SETTING_TIME)
def cmd_set_time(message):
    global time
    # Check if timezone already set
    # I don't remember this if-clause to fire
    if not offset_storage.exists(str(message.chat.id)):
        'No offset storage'
        logger.warning('Whoa! It looks like {0!s} hasn\'t set offset yet! What a shame!'.format(
            message.from_user.username))
        bot.send_message(message.chat.id, config.lang.s_error_timezone_not_set)
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM)
        return None
    timezone = offset_storage.get(str(message.chat.id))
    time = None
    global error_msg
    error_msg = None
    try:
        time = utils.parse_time(message.text, int(timezone))
    except utils.PastDateError as ex:
        error_msg = str(ex)
    except utils.ParseError as ex:
        error_msg = str(ex)
    else:
        pass
    # If there was an error getting time
    if time is None:
        logger.warning(
            'User {0!s} set incorrect time: {1!s}'.format(message.from_user.username, message.text))
        if error_msg is None:
            # "Could not recognize timezone. Please try again"
            bot.send_message(message.chat.id, config.lang.s_error_time_not_recognized)
        else:
            bot.send_message(message.chat.id, error_msg)
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIME)
    else:
        logger.debug('User {0!s} set time: {1!s}'.format(message.from_user.username, time))
        utils.get_time_storage().save(str(message.chat.id), time, force_save=True)
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TEXT)
        bot.send_message(message.chat.id, config.lang.s_common_is_time_correct.format(time))
        pass


# User is satisfied with time and is going to save new note
@bot.message_handler(func=lambda message: state_storage.get(
    str(message.chat.id)) == StateMachine.States.STATE_SETTING_TEXT)
def cmd_save_text(message):
    if len(message.text) > 1000:
        bot.send_message(message.chat.id, config.lang.s_error_note_too_long)
        return None
    global offset_storage
    # Convert user's time to server's local time to set "at" command taking offset into account
    time_to_set = utils.convert_user_time_to_local(utils.get_time_storage().get(str(message.chat.id)), offset_storage.get(key=str(message.chat.id)))
    # Get Unixtime to set to SQLite DB
    unixtime_to_save_to_db = utils.convert_user_time_to_local_timestamp(utils.get_time_storage().get(str(message.chat.id)), offset_storage.get(str(message.chat.id)))
    # Set "at" command and recieve Job ID from it
    job_id = systemtools.set_new_at_job(message.chat.id, time_to_set, message.text.replace('"', r'\"'))
    # Probably this is not the best choice, because some errors can have "job" word in them
    # If not job id provided (error happened or something else)
    if not job_id:
        bot.send_message(message.chat.id, config.lang.s_error_could_not_save_note)
        return None
    logger.info('Successfully set reminder #{0!s} at {1!s}'.format(job_id, time_to_set))
    # Insert new row in table
    mydb = SQLighter(config.database_schedules_file)
    mydb.insert(message.chat.id, unixtime_to_save_to_db, job_id)
    mydb.close()
    bot.send_message(message.chat.id, config.lang.s_common_note_added.format(
        utils.get_time_storage().get(str(message.chat.id))))
    # After setting note, reset to START
    set_new_state(message.chat.id, StateMachine.States.STATE_START)


if __name__ == '__main__':
    utils.init_logger()
    logger = utils.get_logger()
    logger.debug('Logger started')
    utils.init_storage()
    offset_storage = utils.get_offset_storage()
    state_storage = utils.get_state_storage()
    signal.signal(signal.SIGINT, signal_handler)
    bot.polling(none_stop=True)
    while True:
        sleep(60)
        pass
