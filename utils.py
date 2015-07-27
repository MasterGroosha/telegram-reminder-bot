# -*- coding: utf-8 -*-
import logging
import config
import re
from time import mktime, time
from shelver import Shelver
from datetime import datetime, timedelta

DATE_01_01_2017 = 1483218000

TEST_REGEXP_TIME_OR_DATETIME = re.compile(
    r'([01]+[0-9]|2[0-3]):[0-5][0-9]( ([0-2][0-9]|3[0-1]).(0[1-9]|1[0-2]).(201[5-6]|1[5-6]))?')

time_regexp = re.compile(r'([01]+[0-9]|2[0-3]):[0-5][0-9]')
date_regexp = re.compile(
    r'([0-2][0-9]|3[0-1]).(0[1-9]|1[0-2]).(201[5-6]|1[5-6])')
# Нужно для проверки всего сообщения!
date_regexp_enchanced = re.compile(
    r'([01]+[0-9]|2[0-3]):[0-5][0-9] ([0-2][0-9]|3[0-1]).([1-9]|0[1-9]|1[0-2]).(2[0-9][1-9][0-9])')
timezone_regexp = re.compile(r'^0$|^[+-][0-9]$|^[+-]1[0-6]{1}$', re.MULTILINE)
time_lexical_regexp = re.compile(r'(утром|дн[её]м|вечером|ночью)')


class PastDateError(Exception):
    def __init__(self, message):
        self.message = message
        super(PastDateError, self).__init__('{0}'.format(self.message))


class ParseError(Exception):
    def __init__(self, message):
        self.message = message
        super(ParseError, self).__init__('{0}'.format(self.message))


def init_logger():
    global logger
    logger = logging.getLogger(config.log_name)
    logging.basicConfig(filename='decoratorbot.py.log',
                        format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')
    if config.log_level:
        if config.log_level.lower() == 'debug':
            logger.setLevel(logging.DEBUG)
        elif config.log_level.lower() == 'info':
            logger.setLevel(logging.INFO)
        elif config.log_level.lower() == 'warn' or config.log_level.lower() == 'warning':
            logger.setLevel(logging.WARNING)
        elif config.log_level.lower() == 'error':
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.WARNING)


def init_storage():
    global offset_storage
    global time_storage
    offset_storage = Shelver('users_offsets')
    time_storage = Shelver('temp_time_storage')

def get_logger():
    return logger


def get_offset_storage():
    return offset_storage


def get_time_storage():
    global time_storage
    return time_storage


def is_valid_time(text, offset):
    return None


def get_unixtime_now(offset):
    return int(time()) + int(timedelta(hours=int(offset)).seconds)


def get_unixtime_from_date(date_string):
    return int(mktime(datetime.strptime(date_string, '%H:%M %d.%m.%Y').timetuple()))


# Text example: 12:26 20.12.2015, +3
def is_valid_datetime(text, offset):
    try:
        entered_time = get_unixtime_from_date(text)
        if entered_time < get_unixtime_now(offset):
            raise PastDateError('Нельзя указывать дату в прошлом!')
        if entered_time > DATE_01_01_2017:
            raise ParseError('Нельзя указывать дату позднее 01.01.2017')
    except ValueError:
        raise ParseError('Такой даты не существует')
    return True


def parse_time(text, user_timezone):
    global time_regexp
    global potential_result
    probable_text = re.match(time_lexical_regexp, text.lstrip())
    if probable_text is not None:
        probable_text = probable_text.group()
        if probable_text == 'утром':
            print('!!!')
            return '08:00'
        elif probable_text == 'днем' or probable_text == 'днём':
            return '14:00'
        elif probable_text == 'вечером':
            return '20:00'
        elif probable_text == 'ночью':
            return '02:00'

    # TODO: ВНИМАТЕЛЬНО ПРОЧИТАЙ ТО, ЧТО НИЖЕ И РЕАЛИЗУЙ!
    '''
    Поясняю, зачем эта хуйня нужна:
    Короче, может так случиться, что юзер задавал дату и время, а по регулярке
    подходит только время. Это не круто и надо как-то учесть.
    Плюс надо как-то выводить сообщение, поясняющее, что случилась хуйня
    '''

    # Проверяем, указана ли вообще какая-нибудь дата
    # Если нашли Время + Дата
    if re.match(date_regexp_enchanced, text) is not None:
        txt = re.match(date_regexp_enchanced, text).group()
        if is_valid_datetime(txt, user_timezone):
#            get_logger().debug('Datetime valid.Returning {0!s}'.format(txt))
            return txt
        else:
         #   get_logger().debug('Match is not none, but there was error. Returning {0!s}'
         #                      .format(str(txt).split()[0]))
            return str(txt).split()[0]
        pass
    else:
       # get_logger().debug('Something went wrong, Match is none.')
        # Проверяем, что не так:
        if re.match(time_regexp, text) is None:
            raise ParseError('Время отсутствует или указано некорректно')
        else:
          #  get_logger().debug('Ok, returning only time: {0!s}'
         #                      .format(re.match(time_regexp, text).group()))
            # Просто вернём только время, пусть юзер самостоятельно исправляет
            return re.match(time_regexp, text).group()



def parse_timezone(text):
    global timezone_regexp
    match_results = re.match(timezone_regexp, text.lstrip())
    print(match_results)
    if match_results is None:
        return False
    else:
        print('Matching: {0!s}'.format(int(match_results.group())))
        return int(match_results.group())


if __name__ == '__main__':
    pass



