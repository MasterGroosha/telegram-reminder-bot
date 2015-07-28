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
                    format='[%(asctime)s] %(filename)s: %(levelname)s - %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S')
logger.setLevel(logging.INFO)
number_of_deleted = db.delete_old(int(time())).rowcount
# db.commit()  # not for now
logger.info('old_remover executed. Rows deleted: {0!s}'.format(number_of_deleted))