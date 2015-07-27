# -*- coding: utf-8 -*-
from subprocess import call
import tempfile
import sys
from subprocess import call

def set_new_at_job(chat_id, time, text):
    print('Started Systemtools')
    tmp = tempfile.NamedTemporaryFile(mode='r+t')
    text = text.decode('utf-8')
    command = './sender.py {0!s} "\'{1!s}\'"'.format(chat_id, text)
    tmp.write(command)
    call('at {0!s} -f {1!s}'.format(time, tmp.name), shell=True)
    tmp.close()
