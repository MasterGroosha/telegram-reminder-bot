# -*- coding: utf-8 -*-
import sqlite3

# Table structure
# cursor.execute('CREATE TABLE Schedules '
#                '(Id INTEGER PRIMARY KEY, '
#                'Chat_id INTEGER, '
#                'Scheduled_time INTEGER)')

class SQLiteInsertError(Exception):
    def __init__(self, message):
        self.message = message
        super(SQLiteInsertError, self).__init__('{0}'.format(self.message))


class SQLighter:
    """
    Warning! This version works only with one table and fixed columns
    """
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_all(self):
        """
        Get all data from table
        :return:
        """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Schedules').fetchall()

    def select_execution_times(self, starting_from=None):
        """
        Selects "at" executions which will happen in future (if starting_from is set)
        or selects all "at" execution times
        :param starting_from: starting Unix time
        :return: list of execution times or None
        """
        if starting_from:
            result = self.cursor.execute(
                'SELECT Scheduled_time FROM Schedules WHERE Scheduled_time > ?', (starting_from,)) \
                .fetchall()
            if len(result) > 0:
                return result
            else:
                return None
        else:
            result = self.cursor.execute('SELECT Scheduled_time FROM Schedules').fetchall()
            if len(result) > 0:
                return result
            else:
                return None

    def count_entries_for_id(self, chat_id):
        """
        Counts number of entries for specific ID.
        Now non-VIP users can have not more than 5 reminders at once
        :param chat_id:
        :return:
        """
        result = self.cursor.execute('SELECT Id FROM Schedules WHERE Chat_id=?', (int(chat_id),))
        return len(result.fetchall())

    def insert(self, chat_id, time, job_id):
        """
        Creates new entry in table
        :param chat_id: User's chat id
        :param time: Time of execution
        :param job_id: Job ID given by "at" command output
        :return: True if successfully inserted
        :raise SQLiteInsertError: If fail to insert
        """
        with self.connection:
            if self.cursor.execute('INSERT INTO Schedules (Chat_id, Scheduled_time, Job_id) values (?, ?, ?)',
                                   (int(chat_id), int(time), int(job_id))).rowcount < 0:
                raise SQLiteInsertError('Failed to insert data')
            # self.connection.commit()
            return True

    def delete_old(self, time):
        """
        Deletes rows with execution time in the past (related to server's time)
        :param time: Time from which to delete
        :return: ...
        """
        with self.connection:
            result = self.cursor.execute('DELETE FROM Schedules WHERE Scheduled_time < ?', (time,))
            self.connection.commit()
        return result

    def execute(self, code):
        """
        Executes SQL command (use with caution!)
        :param code: SQL command
        """
        with self.connection:
            try:
                self.cursor.execute(code)
            except:
                pass

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


