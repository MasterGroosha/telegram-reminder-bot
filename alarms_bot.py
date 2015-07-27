#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import config, utils, telebot, texts, systemtools
from time import sleep
from SQLighter import SQLighter

users_that_is_setting_time = []
users_that_is_setting_timezone = []
users_that_is_going_to_confirm_time = []

bot = telebot.TeleBot(config.token)
global offset_storage
global logger


@bot.message_handler(commands=['start'])
def command_help(message):
    logger.debug('User {0!s} started new chat with bot'.format(message.chat.id))
    bot.send_message(message.chat.id, texts.welcome_text)


@bot.message_handler(commands=['newalarm'])
def cmd_new_alarm(message):
    # Подчищаем хвосты с прошлых запросов
    if message.chat.id in users_that_is_setting_timezone:
        users_that_is_setting_timezone.remove(message.chat.id)
    if message.chat.id in users_that_is_setting_time:
        users_that_is_setting_time.remove(message.chat.id)

    # Проверка, указывал юзер часовой пояс или нет
    # Если не указывал -> отправляем указывать
    if not offset_storage.exists(str(message.chat.id)):
        logger.debug('User {0!s} is going to set new alarm. It\'s his first appear'.format(message.chat.id))
        users_that_is_setting_timezone.append(message.chat.id)
        bot.send_message(message.chat.id, texts.guide_timezone)
    # Если в системе уже сохранен его часовой пояс - сразу предлагаем установить время заметки
    else:
        logger.debug('User {0!s} is going to set new alarm. He has been here before'.format(message.chat.id))
        users_that_is_setting_time.append(message.chat.id)
        bot.send_message(message.chat.id, texts.guide_time)


@bot.message_handler(commands=['setoffset'])
def cmd_set_offset(message):
    logger.debug('User {0!s} is going to set offset'.format(message.chat.id))
    if message.chat.id not in users_that_is_setting_timezone:
        users_that_is_setting_timezone.append(message.chat.id)
    bot.send_message(message.chat.id, texts.guide_timezone)


@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    # Убираем его отовсюду, откуда можем
    if message.chat.id in users_that_is_setting_time:
        users_that_is_setting_time.remove(message.chat.id)
    if message.chat.id in users_that_is_setting_timezone:
        users_that_is_setting_timezone.remove(message.chat.id)
    if message.chat.id in users_that_is_going_to_confirm_time:
        users_that_is_going_to_confirm_time.remove(message.chat.id)
    logger.debug('User {0!s} cancelled current task'.format(message.chat.id))
    bot.send_message(message.chat.id, 'Хорошо. Давайте начнём всё сначала.')


# Если юзер в списке устанавливающий часовой пояс
@bot.message_handler(func=lambda message: message.chat.id in users_that_is_setting_timezone)
def cmd_update_timezone_for_user(message):
    # Пытаемся распознать его сообщение
    timezone = utils.parse_timezone(message.text)
    if timezone is None:
        bot.send_message(message.chat.id,
                         'Не получилось распознать часовой пояс, попробуйте ещё раз')
        return None
    else:
        logger.debug('User set timezone: {0!s}'.format(timezone))
        offset_storage.save(key=str(message.chat.id), value=timezone, force_save=True)
        print(offset_storage.get(str(message.chat.id)))
        bot.send_message(message.chat.id, 'Часовой пояс сохранён, спасибо!')
        if message.chat.id in users_that_is_setting_timezone:
            users_that_is_setting_timezone.remove(message.chat.id)
        cmd_new_alarm(message)


@bot.message_handler(func=lambda message: message.chat.id in users_that_is_setting_time)
def cmd_update_timezone_for_user(message):
    global time
    # Check if timezone already set
    if not offset_storage.exists(str(message.chat.id)):
        logger.warning('Whoa! It looks like {0!s} hasn\'t set offset yet! What a shame!'.format(
            message.chat.id))
        bot.send_message(message.chat.id,
                         'Вы не установили часовой пояс. Пожалуйста, установите его при помощи команды /setoffset и попробуйте ещё раз')
        return None
    else:
        # TODO: ЗАЧЕМ?
        if message.chat.id in users_that_is_setting_timezone:
            users_that_is_setting_timezone.remove(message.chat.id)
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
            bot.send_message(message.chat.id, 'Не удалось распознать время, попробуйте ещё раз.')
        else:
            bot.send_message(message.chat.id, error_msg)
    else:
        # Если хоть что-то верно, пусть юзеру выводится сообщение
        if message.chat.id in users_that_is_setting_time:
            users_that_is_setting_time.remove(message.chat.id)
        utils.get_time_storage().save(str(message.chat.id), time, force_save=True)
        users_that_is_going_to_confirm_time.append(message.chat.id)
        bot.send_message(message.chat.id, texts.reply_is_correct_time.format(time))
        pass


# Если юзера удовлетворило время и он пишет заметку
@bot.message_handler(func=lambda message: message.chat.id in users_that_is_going_to_confirm_time)
def cmd_save_text(message):
    if len(message.text) > 1000:
        bot.send_message(message.chat.id, texts.reply_too_long_note)
        return None
    systemtools.set_new_at_job(message.chat.id, utils.get_time_storage().get(str(message.chat.id)), message.text)
    try:
        del utils.get_time_storage()[str(message.chat.id)]
    except:
        pass
    # TODO: НАПИСАТЬ ДОБАВЛЕНИЕ ЗАМЕТКИ
    pass

if __name__ == '__main__':
    utils.init_logger()
    logger = utils.get_logger()
    logger.debug('Logger started')
    utils.init_storage()
    offset_storage = utils.get_offset_storage()
    logger.debug('Storage is open now')

    bot.polling(none_stop=True, interval=5)
    while True:
        sleep(60)
        pass