#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import sys
from time import sleep
import signal

import telebot
import config
import utils
import texts
import systemtools
import StateMachine

bot = telebot.TeleBot(config.token)
global offset_storage
global logger
global state_storage


# Обработчик KeyboardInterrupt
def signal_handler(signal, frame):
    logger.info('Signal catched, closing databases')
    print('Signal catched, closing databases')
    utils.close_storages()
    sys.exit(0)

# A simple wrapper to set state (inside uses my Shelver)
def set_new_state(chat_id, state_name):
    state_storage.save(str(chat_id), state_name, force_save=True)


@bot.message_handler(commands=['start'])
def command_help(message):
    logger.debug('User {0!s} started new chat with bot'.format(message.chat.id))
    # I don't know why to use START state, but why not?
    set_new_state(message.chat.id, StateMachine.States.STATE_START)
    bot.send_message(message.chat.id, texts.welcome_text)


# User is going to set alarm
@bot.message_handler(commands=['newalarm'])
def cmd_new_alarm(message):
    set_new_state(message.chat.id, StateMachine.States.STATE_NEWALARM)

    # Проверка, указывал юзер часовой пояс или нет
    # Если не указывал -> отправляем указывать
    if not offset_storage.exists(str(message.chat.id)):
        logger.debug('User {0!s} is going to set new alarm. It\'s his first appear'.format(message.chat.id))
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM)
        bot.send_message(message.chat.id, texts.guide_timezone)
    # Если в системе уже сохранен его часовой пояс - сразу предлагаем установить время заметки
    else:
        logger.debug('User {0!s} is going to set new alarm. He has been here before'.format(message.chat.id))
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIME)
        bot.send_message(message.chat.id, texts.guide_time)


# Standalone timezone setting. See below for explanation
@bot.message_handler(commands=['setoffset'])
def cmd_set_offset(message):
    logger.debug('User {0!s} is going to set offset'.format(message.chat.id))
    set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIMEZONE_SEPARATE)
    bot.send_message(message.chat.id, texts.guide_timezone)


# If cancel - reset state
@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    set_new_state(message.chat.id, StateMachine.States.STATE_START)
    logger.debug('User {0!s} cancelled current task'.format(message.chat.id))
    bot.send_message(message.chat.id, 'Хорошо. Давайте начнём всё сначала.')


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
        bot.send_message(message.chat.id,
                         'Не получилось распознать часовой пояс, попробуйте ещё раз')
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM)
        return None
    else:
        logger.debug('User set timezone: {0!s}'.format(timezone))
        offset_storage.save(key=str(message.chat.id), value=timezone, force_save=True)
        if state_storage.get(str(message.chat.id)) == StateMachine.States.STATE_SETTING_TIMEZONE_FOR_ALARM:
            bot.send_message(message.chat.id, texts.guide_time)
            set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIME)
        if state_storage.get(str(message.chat.id)) == StateMachine.States.STATE_SETTING_TIMEZONE_SEPARATE:
            # "Timezone saved. Thank you!"
            bot.send_message(message.chat.id, 'Часовой пояс сохранён, спасибо!')
            set_new_state(message.chat.id, StateMachine.States.STATE_START)


# User is setting time
@bot.message_handler(func=lambda message: state_storage.get(
    str(message.chat.id)) == StateMachine.States.STATE_SETTING_TIME)
def cmd_set_time(message):
    print('Begin set time')
    global time
    # Check if timezone already set
    # I don't remember this if-clause to fire
    if not offset_storage.exists(str(message.chat.id)):
        'No offset storage'
        logger.warning('Whoa! It looks like {0!s} hasn\'t set offset yet! What a shame!'.format(
            message.chat.id))
        # "You haven't set timezone. Please, set it with /setoffset and try again"
        bot.send_message(message.chat.id,
                         'Вы не установили часовой пояс. Пожалуйста, установите его при помощи команды /setoffset и попробуйте ещё раз')
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
    if time is None:
        logger.warning(
            'User {0!s} set incorrect time: {1!s}'.format(message.chat.id, message.text))
        if error_msg is None:
            # "Could not recognize timezone. Please try again"
            bot.send_message(message.chat.id, 'Не удалось распознать время, попробуйте ещё раз.')
        else:
            bot.send_message(message.chat.id, error_msg)
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TIME)
    else:
        utils.get_time_storage().save(str(message.chat.id), time, force_save=True)
        set_new_state(message.chat.id, StateMachine.States.STATE_SETTING_TEXT)
        bot.send_message(message.chat.id, texts.reply_is_correct_time.format(time))
        pass


# User is satisfied with time and is going to save new note
@bot.message_handler(func=lambda message: state_storage.get(
    str(message.chat.id)) == StateMachine.States.STATE_SETTING_TEXT)
def cmd_save_text(message):
    if len(message.text) > 1000:
        bot.send_message(message.chat.id, texts.reply_too_long_note)
        return None
    systemtools.set_new_at_job(message.chat.id, utils.get_time_storage().get(str(message.chat.id)), message.text)
    # After setting note, reset to START
    set_new_state(message.chat.id, StateMachine.States.STATE_START)


if __name__ == '__main__':
    utils.init_logger()
    logger = utils.get_logger()
    logger.debug('Logger started')
    utils.init_storage()
    offset_storage = utils.get_offset_storage()
    logger.debug('Storage is open now')
    state_storage = utils.get_state_storage()
    signal.signal(signal.SIGINT, signal_handler)
    bot.polling(none_stop=True)
    while True:
        sleep(60)
        pass
