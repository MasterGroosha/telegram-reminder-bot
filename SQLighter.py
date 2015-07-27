# -*- coding: utf-8 -*-
import sqlite3


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
    ВНИМАНИЕ! В данной реализации класс работает только с одной таблицей!
    """
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_all(self):
        """
        Выборка всех данных из таблицы
        :return:
        """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Schedules').fetchall()

    def select_execution_times(self, starting_from=None):
        if starting_from:
            result = self.cursor.execute(
                'SELECT Scheduled_time FROM Schedules WHERE Scheduled_time > ?', (starting_from,)) \
                .fetchall()
            if len(result) > 0:
                print('Len = {0!s}'.format(len(result)))
                return result
            else:
                return None
        else:
            result = self.cursor.execute('SELECT Scheduled_time FROM Schedules').fetchall()
            if len(result) > 0:
                print('Len = {0!s}'.format(len(result)))
                return result
            else:
                return None

    def count_entries_for_id(self, chat_id):
        result = self.cursor.execute('SELECT Id FROM Schedules WHERE Chat_id=?', (chat_id,))
        return len(result.fetchall())

    def insert(self, chat_id, time):
        with self.connection:
            if self.cursor.execute('INSERT INTO Schedules (Chat_id, Scheduled_time) values (?, ?)',
                                   (chat_id, time)).rowcount < 0:
                raise SQLiteInsertError('Failed to insert data')
            return True

    # def update ??

    def delete_old(self, time):
        with self.connection:
            self.cursor.execute('DELETE FROM Schedules WHERE Scheduled_time < ?', (time,))
        return True

    def execute(self, code):
        with self.connection:
            try:
                self.cursor.execute(code)
            except:
                pass

    def close(self):
        self.connection.close()


