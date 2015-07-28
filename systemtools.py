# -*- coding: utf8 -*-
import tempfile
from subprocess import call

def set_new_at_job(chat_id, time, text):
    """
    Sets new "at" job in Linux (man at for more)
    :param chat_id: User's chat_id
    :param time: time in HH:MM DD.MM.YYYY format
    :param text: text to send to user
    :return: "at" command's job id / None if error occured
    """
    tmp = tempfile.NamedTemporaryFile(mode='r+t')
    # Actually, sender.py will send message
    command = 'echo "./sender.py {0!s} \'{2!s}\'" | at {1!s}'.format(chat_id, time, text)
    # Because of some warnings, all data is sent to stderr instead of stdout.
    # But it's normal
    call(command, shell=True, stderr=tmp)
    tmp.seek(0)
    for line in tmp:
        if 'job' in line:
            return line.split()[1]
    tmp.close()
    return None
