#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from inspect import getmembers, isfunction
from pathlib import Path
from threading import RLock

from ._cache import _DecoratorsCache

_DECORATORS_IMPL_MAP_KEY = "decorators-impl-map-key"
_DECORATORS_NAME_KEY = "decorators-name-key"
_EXCLUDE_MODULES = ("simplebox.decorators", "simplebox.decorators._process", "simplebox.decorators._cache",
                    "simplebox.decorators._hook", "simplebox.decorators._singleton")
_STACK_LEVEL_DEFAULT = 5

from ._around import around
from ._capture import capture
from ._loop import retry, retrying, repeat, repeating
from ._singleton import single
from ._validate import validate, Valid
from ._properties import PropertySource, Entity, EntityType
from ._shape import shaper
from ._ticker import ticker_apply, ticker_apply_async
from ._scheduler import scheduler_sync, scheduler_async, scheduler_sync_process, scheduler_async_process, \
    scheduler_asyncio, scheduler_gevent
from ._simplelog import simplelog


class _ScanModule(object):
    """
    scan decorators execute function
    """
    __lock = RLock()
    __instance = None

    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.__decorators_impl_map = {}
        self.__build()

    def __build(self):
        for name, module in sys.modules.items():
            #  noinspection PyBroadException
            try:
                if Path(module.__file__).parent == Path(__file__).parent and name not in _EXCLUDE_MODULES:
                    for f_name, f_object in getmembers(module, isfunction):
                        if f_name.startswith("__do_"):
                            self.__decorators_impl_map[f_name.split("__do_")[1]] = {f_object: None}
            except BaseException:
                pass
        _DecoratorsCache.put(_DECORATORS_IMPL_MAP_KEY, self.__decorators_impl_map)
        _DecoratorsCache.put(_DECORATORS_NAME_KEY, list(self.__decorators_impl_map.keys()))

    @property
    def decorators_impl(self) -> dict:
        return self.__decorators_impl_map

    @property
    def decorators(self) -> list:
        for decorator in self.__decorators_impl_map.keys():
            yield decorator


_ScanModule()

__all__ = ["around", "capture", "retry", "retrying", "repeat", "repeating", "single", "validate",
           "Valid", "PropertySource", "Entity", "EntityType", "shaper", "ticker_apply", "ticker_apply_async",
           "scheduler_sync", "scheduler_async", "scheduler_sync_process", "scheduler_async_process",
           "scheduler_asyncio", "scheduler_gevent", "simplelog"]
