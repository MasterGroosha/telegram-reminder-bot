#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
"""
Removes outdated entries from DB (used to lower usage count)
"""
from config import database_schedules_file, log_name
from SQLighter import SQLighter
from time import time

db = SQLighter(database_schedules_file)
import logging

logger = logging.getLogger(log_name)
logging.basicConfig(filename=log_name + '.log',
                    format='[%(asctime)s] OLD_REMOVER %(levelname)s - %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S')
logger.setLevel(logging.INFO)
try:
    number_of_deleted = db.delete_old(int(time())).rowcount
    logger.info('Finished processing old rows. Rows deleted: {0!s}'.format(number_of_deleted))
except Exception as ex:
    logger.error('Failed to process old rows: {0!s}'.format(str(ex)))
