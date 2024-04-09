#!/usr/bin/env python
# -*- coding:utf-8 -*-
from contextlib import contextmanager
from multiprocessing import RLock as PLock
from multiprocessing import Manager
from random import choice
from threading import RLock as TLock
from typing import TypeVar

from gevent.lock import RLock as CLock

from ..exceptions import NotFountException
from ..utils.objects import ObjectsUtils

T = TypeVar("T", TLock, PLock, CLock)


class Sentry(object):
    """
    lock by variable.
    Theoretically, objects can be locked in this way.
    For example, file locking.
    """

    def __init__(self, lock, free):
        self.__lock: T = lock
        self.__free: list = free

    def add(self, *obj):
        """
        add element(s)
        """
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        self.__free.extend(obj)
        self.__lock.release()

    def add_item(self, item):
        """
        batch call add()
        """
        self.add(*item)

    @contextmanager
    def draw(self):
        """
        Consume an element randomly
        :return:
        """
        obj = None
        self.__lock.acquire()
        size = len(self.__free)
        if size > 0:
            obj = choice(self.__free)
        yield obj
        self.__lock.release()

    @contextmanager
    def pick(self, value, null=True):
        """
        Provide an object to consume from the lock
        :params null: if True, returns None when the element does not exist, otherwise an exception is thrown
        """
        obj = None
        self.__lock.acquire()
        size = len(self.__free)
        if size > 0:
            # noinspection PyBroadException
            try:
                index = self.__free.index(value)
                obj = self.__free.pop(index)
            except BaseException:
                if null is not True:
                    raise NotFountException(f"not found element: {value}")
        yield obj
        self.__lock.release()


class _Singleton(type):
    """
    singletons
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Locks(metaclass=_Singleton):
    """
    Built-in lock type
    """

    @staticmethod
    def process() -> Sentry:
        """
        multi processing lock
        """
        manager = Manager()
        free: set = manager.list()
        lock: T = PLock()
        return Sentry(lock, free)

    @staticmethod
    def thread() -> Sentry:
        """
        multi thread lock

        """
        return Sentry(TLock(), [])

    @staticmethod
    def coroutine() -> Sentry:
        """
        coroutine lock
        """
        return Sentry(CLock(), [])


__all__ = [Locks, Sentry]
