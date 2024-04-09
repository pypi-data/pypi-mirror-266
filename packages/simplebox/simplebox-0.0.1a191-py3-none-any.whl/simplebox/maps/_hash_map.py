#!/usr/bin/env python
# -*- coding:utf-8 -*-
from .._pypkg import Callable

from ..collection.collectors import Stream
from ..generic import V, K
from ..maps._map import Map


class HashMap(Map[K, V]):

    def __init__(self, dictionary: dict[K, V] = None, factory: Callable = None, **kw):
        """
        The factory is called without arguments to produce
        a new value when a key is not present, in __getitem__ only.
        A HashMap compares equal to a dict with the same items.
        All remaining arguments are treated the same as if they were
        passed to the dict constructor, including keyword arguments.
        example:
            hash_map = HashMap({"a": "a"}, str)
            print(hash_map["b"]) => ''
            print(hash_map) => HashMap({'a': 'a', 'b': ''})
        """
        self.__factory = factory
        m = dictionary or {}
        m.update(kw)
        super().__init__(m)

    def __delitem__(self, key):
        if self.contain_key(key):
            super().__delitem__(key)
        else:
            raise KeyError(f"not found '{key}' in {self}")

    def __setitem__(self, key: K, value: V):
        super().__setitem__(key, value)

    def __getitem__(self, key: K) -> V:
        if key in self:
            return super().__getitem__(key)
        else:
            if not callable(self.__factory):
                raise KeyError(f"'{key}'")
            v = self.__factory()
            super().__setitem__(key, v)
            return v

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"

    @staticmethod
    def of_dictionary(dictionary: dict[K, V], factory: Callable = None) -> 'HashMap[K, V]':
        return HashMap(dictionary=dictionary, factory=factory)

    @staticmethod
    def of_kwargs(factory: Callable = None, **kwargs) -> 'HashMap[K, V]':
        return HashMap(dictionary=kwargs, factory=factory)

    @staticmethod
    def of_empty(factory: Callable = None) -> 'HashMap[K, V]':
        return HashMap(factory=factory)

    def merge(self, other: dict[K, V]) -> 'HashMap[K, V]':
        return HashMap(dict(self, **other))

    def update(self, other: dict[K, V], **kwargs: [K, V]) -> 'HashMap[K, V]':
        if isinstance(other, dict):
            self.update(other)
        self.update(kwargs)
        return self

    def put(self, key: K, value: V) -> V:
        v = self.get(key)
        super().__setitem__(key, value)
        return v

    def put_if_absent(self, key: K, value: V) -> V:
        v = self.get(key)
        if key not in self:
            super(HashMap, self).__setitem__(key, value)
        return v

    def remove(self, key: K, default: V = None) -> V:
        return super().pop(key, default)

    def remove_value_none(self) -> 'HashMap[K, V]':
        return self.remove_if_predicate(lambda k, v: v is None)

    def remove_if_predicate(self, predicate: Callable[[K, V], bool]) -> 'HashMap[K, V]':
        rm = HashMap()
        for k, v in self.items():
            if predicate(k, v):
                rm[k] = v
                del self[k]
        return rm

    def size(self) -> int:
        return len(self)

    def items(self) -> Stream[list[(K, V)]]:
        return super(HashMap, self).items()

    def keys(self) -> Stream[K]:
        return super(HashMap, self).keys()

    def values(self) -> Stream[V]:
        return super(HashMap, self).values()

    def contain_key(self, key):
        return key in self.keys()

    def contain_value(self, value):
        return value in self.values()

    def for_each(self, action: Callable[[K, V], None]):
        for k, v in self.items():
            action(k, v)


__all__ = [HashMap]
