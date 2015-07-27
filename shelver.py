# -*- coding: utf-8 -*-
import shelve
from re import match


class SaveValueError(Exception):
    def __init__(self, message):
        self.message = message
        super(SaveValueError, self).__init__('{0}'.format(self.message))


class GetValueError(Exception):
    def __init__(self, message):
        self.message = message
        super(GetValueError, self).__init__('{0}'.format(self.message))


class NoKeyError(Exception):
    def __init__(self, message):
        self.message = message
        super(NoKeyError, self).__init__('{0}'.format(self.message))


class Shelver:
    def __init__(self, database):
        self.storage = shelve.open(database)

    def create_key(self, key):
        """
        Создает ключ без значения
        :param key:
        """
        self.storage[key] = None
        return True

    def save(self, key, value, force_save=False):
        if not self.exists(key) and force_save is False:
            raise NoKeyError('No such key: {0!s}'.format(key))
        if not self.exists(key) and force_save is True:
            self.create_key(key)
            self.save(key, value)
            return True
        if self.exists(key):
            try:
                self.storage[key] = value
                return True
            except Exception as ex:
                raise SaveValueError('{0}: {1}'.format(type(ex).__name__, 'failed to save value'))

    def get(self, key):
        """
        Получает значение из хранилища по ключу.
        В случае, если ключ не существует, бросает исключение NoKeyError
        :param key:
        :return: Значение по заданному ключу
        :raise NoKeyError: Если ключ отсутствует в хранилище
        """
        if key in self.storage:
            return self.storage[key]
        else:
            raise NoKeyError('No such key in offset_storage: ' + str(key))

    def get_with_create(self, key, default):
        """
        Получает значение из хранилища по ключу.
        В случае, если ключ не существует, создает, присваивает значение default
        и возвращает его
        :param key: ключ, по которому ищем
        :param default: значение, устанавливаемое ключу, если его не существует
        :return: значение по ключу
        """
        try:
            if key in self.storage and not None:
                value = self.storage[key]
                return value
            else:
                self.storage[key] = default
                return default
        except Exception as ex:
            raise GetValueError(
                '{0}: {1}'.format(type(ex).__name__, 'failed to get value from offset_storage'))

    def append(self, key, value, strict=True):
        """
        Получает значение по ключу как список и добавляет туда значение
        :param strict: Если True, то отсутствие ключа приводит к исключению,
        Если False, то создается новый ключ с данным названием
        :param key: ключ, по которому ищем
        :param value: значение, добавляемое в список
        :return: :raise NoKeyError:
        """
        if strict and key not in self.storage:
            raise NoKeyError('No such key in offset_storage: ' + str(key))
        else:
            tmp = list(self.get_with_create(key, []))
            tmp.append(value)
            self.save(key, tmp)
            return True

    def remove(self, key, value):
        """
        Получает значение по ключу как список и удаляет оттуда значение value
        Если такого значения в списке не было, ничего не делаем
        :param key: ключ, по которому ищем
        :param value: значение, удаляемое из списка
        :return: :raise NoKeyError:
        """
        if key in self.storage:
            tmp = list(self.storage[key])
            if value in tmp:
                tmp.remove(value)
            self.save(key, tmp)
            return True
        else:
            raise NoKeyError('No such key in offset_storage: ' + str(key))

    def find_all(self, pattern):
        """
        Находит все ключи по заданному шаблону
        :param pattern: шаблон (регулярное выражение)
        :return: массив ключей, подходящих по шаблону
        """
        keys = self.storage.keys()
        result = []
        for k in keys:
            if match(pattern, k):
                result.append(k)
        return result

    def find_single(self, pattern):
        """
        Находит первый попавшийся ключ по заданному шаблону
        :param pattern: шаблон (регулярное выражение)
        :return: первое найденное значение по шаблону или ничего
        """
        keys = self.storage.keys()
        for k in keys:
            if match(pattern, k):
                return k
        else:
            return None

    def exists(self, key):
        if key in self.storage.keys():
            return True
        else:
            return False


if __name__ == '__main__':
    s = Shelver('testdb')
    s.create_key('test1')
    print(s.exists('test1'))
    print(s.exists('test2'))
