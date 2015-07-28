# -*- coding: utf-8 -*-
"""
My custom wrapper for shelve module
"""
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
        creates key without value
        :param key: key name
        """
        self.storage[key] = None
        return True

    def save(self, key, value, force_save=False):
        """
        Saves value for key.
        :param key: key name
        :param value: value to save
        :param force_save: if False, raise NoKeyError when key doesn't exist
        if True, creates key and saves value to it
        :return: True, if value is saved
        :raise SaveValueError: when fail to save key
        :raise NoKeyError: if key doesn't exist and force_save == False
        """
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
        Gets value from key.
        If key doesn't exist, throws NoKeyError
        :param key: key name
        :return: value for that key
        :raise NoKeyError: if key doesn't exist
        """
        if key in self.storage:
            return self.storage[key]
        else:
            raise NoKeyError('No such key in offset_storage: ' + str(key))

    def get_with_create(self, key, default):
        """
        Gets value from key.
        If key doesn't exist, creates one with "default" value and returns it
        :param key: key name
        :param default: if key doesn't exist, default value for new key with "key" name
        :return: value for that key
        """
        try:
            if key in self.storage and not None:
                value = self.storage[key]
                return value
            else:
                self.create_key(key)
                self.save(key, default)
                return default
        except Exception as ex:
            raise GetValueError(
                '{0}: {1}'.format(type(ex).__name__, 'failed to get value from offset_storage'))

    def append(self, key, value, strict=True):
        """
        Gets list for key and appends "value" to it
        :param strict: if True, raise NoKeyError, if key doesn't exist
        if False, create key with "value" value
        :param key: key name
        :param value: value to append
        :return: True if value appended
        :raise NoKeyError: if key doesn't exist
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
        Gets list for key and removes "value" value from it
        If there's no such value in list, do nothing
        :param key: key name
        :param value: value to remove
        :return: True, if value is removed
        :raise NoKeyError: if no such key in storage
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
        Finds all keys mathing desired pattern
        :param pattern: pattern (regular expression)
        :return: list of keys matching pattern
        """
        keys = self.storage.keys()
        result = []
        for k in keys:
            if match(pattern, k):
                result.append(k)
        return result

    def find_single(self, pattern):
        """
        Finds first key mathing desired pattern
        :param pattern: pattern (regular expression)
        :return: first matching key or None
        """
        keys = self.storage.keys()
        for k in keys:
            if match(pattern, k):
                return k
        else:
            return None

    def exists(self, key):
        """
        Checks, if key exists in storage
        :param key: key name
        :return: True if key exists; False if doesn't
        """
        if key in self.storage.keys():
            return True
        else:
            return False

    def close(self):
        self.storage.close()

