#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from typing import Any
from operator import contains, eq

from . import _DecoratorsCache, _DECORATORS_NAME_KEY, _DECORATORS_IMPL_MAP_KEY, _STACK_LEVEL_DEFAULT
from ._tools import AstTools


def _do(func, decorator_name, args, kwargs, opts: dict = None) -> Any:
    """
    Decorator master. Assign the executor of the decorator.
    :param func: origin function.
    :param decorator_name: the name of the decorator on the function.
    :param args: origin function's args.
    :param kwargs: origin function's kwargs.
    :return: origin function return value
    """
    func_full_name: str = func.__qualname__
    module = sys.modules[func.__module__]
    if "." in func_full_name:
        class_name = func_full_name.split(".")[0]
        clz = getattr(module, class_name, None)
    else:
        clz = func
    if clz is None:
        raise ValueError("method's class is None")
    decorator_name_list_tmp = []
    if _DecoratorsCache.has_cache(func):
        decorator_name_list_tmp = _DecoratorsCache.get(func)
    else:
        decorator_name_list = AstTools(clz).get_decorator_of_function_by_name(func.__name__)
        if not decorator_name_list:
            return func(*args, **kwargs)
        for decorator in decorator_name_list:
            if decorator in _DecoratorsCache.get(_DECORATORS_NAME_KEY):
                decorator_name_list_tmp.append(decorator)
        _DecoratorsCache.put(func, decorator_name_list_tmp)
    process_map = _DecoratorsCache.get(_DECORATORS_IMPL_MAP_KEY).get(decorator_name, {})
    for decorator_func, _ in process_map.items():
        process_map[decorator_func] = opts
        break
    result = None
    if decorator_name_list_tmp and decorator_name_list_tmp[-1] == decorator_name:
        stacklevel = _STACK_LEVEL_DEFAULT + (len(decorator_name_list_tmp) - 1) * 2
        for decorator in decorator_name_list_tmp:
            process_map: dict = _DecoratorsCache.get(_DECORATORS_IMPL_MAP_KEY)[decorator]
            for decorator_func, decorator_func_opts in process_map.items():
                if eq("__do_simplelog", decorator_func.__name__):
                    if contains(decorator_func_opts, "stacklevel") and decorator_func_opts.get("stacklevel") is None:
                        decorator_func_opts["stacklevel"] = stacklevel
                result = decorator_func(func, args=args, kwargs=kwargs, opts=decorator_func_opts)
                break
    else:
        result = func(*args, **kwargs)
    return result
