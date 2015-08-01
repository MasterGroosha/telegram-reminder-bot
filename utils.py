# -*- coding: utf-8 -*-
import logging
import config
import re
from time import mktime, time, strftime
from shelver import Shelver
from datetime import datetime
from SQLighter import SQLighter

DATE_01_01_2017 = 1483218000
SECONDS_IN_24_HOURS = 86401

time_regexp = re.compile(r'([01]+[0-9]|2[0-3]):[0-5][0-9]')
# Нужно для проверки всего сообщения!
date_regexp_enchanced = re.compile(
    r'([01]+[0-9]|2[0-3]):[0-5][0-9] ([0-2][0-9]|3[0-1]).([1-9]|0[1-9]|1[0-2]).(2[0-9][1-9][0-9])')
timezone_regexp = re.compile(r'0|[+-][0-9]|[+-]1[0-6]{1}', re.MULTILINE)


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
    logging.basicConfig(filename=config.log_name + '.log',
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


# TODO: РАЗОБРАТЬСЯ, КАКОЙ ФАЙЛ ЗА ЧТО ОТВЕЧАЕТ
def init_storage():
    global offset_storage
    global time_storage
    global state_storage
    global db
    offset_storage = Shelver(config.database_offsets_file)
    time_storage = Shelver(config.database_temp_time_storage)
    state_storage = Shelver(config.database_states_file)
    db = SQLighter(config.database_schedules_file)


def get_logger():
    return logger


def get_offset_storage():
    return offset_storage


def get_time_storage():
    global time_storage
    return time_storage


def get_state_storage():
    global state_storage
    return state_storage


def get_database():
    global db
    return db


def close_storages():
    get_time_storage().close()
    get_state_storage().close()
    get_offset_storage().close()
    db.close()


def get_unixtime_from_date(date_string):
    """
    Gets Unixtime from string
    :param date_string: string in HH:MM dd.mm.YYYY format (20:00 29.12.2015)
    :return: Unixtime based on date_string
    """
    return int(mktime(datetime.strptime(date_string, '%H:%M %d.%m.%Y').timetuple()))


def get_user_date(offset):
    """
    Gets user's current date (taking into account offset)
    :param offset: Timezone difference with Moscow (GMT +3)
    :return:
    """
    return datetime.fromtimestamp(int(time()) + (3600 * offset) - (3600 * config.server_offset)).strftime('%d.%m.%Y')

def convert_user_time_to_local(text, offset):
    """
    Converts user's entered time to server's local time (to set "at" command)
    :param text: string in HH:MM dd.mm.YYYY format (20:00 29.12.2015)
    :param offset: Timezone difference with Moscow (GMT +3)
    :return:
    """
    if offset == 0:
        return text
    return datetime.fromtimestamp(get_unixtime_from_date(text) - (3600 * offset)).strftime('%H:%M %d.%m.%Y')


def convert_user_time_to_at_command(text, offset):
    """

    :param text:
    :param offset:
    :return:
    """
    if int(offset) == config.server_offset:
        return text
        #return strftime('{0!s} + {1!s} hours'.format(text, config.server_offset))
    elif int(offset) > config.server_offset:
        return strftime('{0!s} - {1!s} hours'.format(text, offset - config.server_offset))
    elif int(offset) < config.server_offset:
        return strftime('{0!s} + {1!s} hours'.format(text, -offset + config.server_offset))


def convert_user_time_to_local_timestamp(text, offset):
    """
    Returns server's local unixtime for entered string date
    :param text: string in HH:MM dd.mm.YYYY format (20:00 29.12.2015)
    :param offset: Timezone difference with Moscow (GMT +3)
    :return:
    """
    return get_unixtime_from_date(text) - (3600 * offset)


# Text example: 12:26 20.12.2015, +3
def is_valid_datetime(text, offset):
    """
    Checks date validity:
    1. Date is not in the past
    2. Not more than 01.01.2017
    :param text: string in HH:MM dd.mm.YYYY format (20:00 29.12.2015)
    :param offset: Timezone difference with Moscow (GMT +3)
    :return: True
    :raise ParseError: If entered date is incorrect
    """
    try:
        entered_time = get_unixtime_from_date(text)
        if (entered_time - (3600 * offset)) < (time() - (3600 * config.server_offset)):
            raise PastDateError(config.lang.s_error_date_in_past)
        if entered_time > DATE_01_01_2017:
            raise ParseError(config.lang.s_error_after_2017)
    except ValueError:
        raise ParseError(config.lang.s_error_incorrect_date)
    except OverflowError:
        raise ParseError(config.lang.s_error_incorrect_input)
    return True


def parse_time(text, user_timezone):
    """
    Main checking function
    If user entered time AND date, checks its validity
    If only time entered, finds out user's date and appends to time
    :param text: string in HH:MM dd.mm.YYYY or HH:MM format (20:00 29.12.2015 or 20:00)
    :param user_timezone: user's timezone
    :return: string in HH:MM dd.mm.YYYY format
    :raise ParseError: on validation error
    """
    global time_regexp
    if re.search(date_regexp_enchanced, text) is not None:
        txt = re.search(date_regexp_enchanced, text).group()
        if is_valid_datetime(txt, user_timezone):
            return txt
        else:
            raise ParseError(config.lang.s_error_incorrect_input)
    else:
        # Если есть хотя бы время
        if re.search(time_regexp, text) is not None:
            time_with_date = \
                str(re.search(time_regexp, text).group()) + ' ' + get_user_date(user_timezone)
            if is_valid_datetime(time_with_date, user_timezone):
                return time_with_date
            else:
                raise ParseError(config.lang.s_error_incorrect_input)


def parse_timezone(text):
    """
    Checks entered timezone validity (not more than +/- 16)
    :param text: (string) timezone (+3, 0, -5 ...)
    :return: (int) timezone value / False on validation error
    """
    global timezone_regexp
    match_results = re.search(timezone_regexp, text.lstrip())
    if match_results is None:
        try:
            num = int(text.lstrip())
            if -16 < num < 16:
                return num
            else:
                return None
        except Exception:
            get_logger().warning('Could not recognize timezone: {0!s}'.format(text.lstrip()))
            return None
    else:
        return int(match_results.group())


if __name__ == '__main__':
    #print(parse_time('22:32 29.07.2015',3))
    print(get_user_date(5))
    pass

