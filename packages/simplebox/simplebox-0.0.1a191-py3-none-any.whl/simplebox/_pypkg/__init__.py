#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
The import that talks about some version differences is placed here.
"""
from ..version import check_py_version_lt
if check_py_version_lt("3.10"):
    from typing import Callable
else:
    from collections.abc import Callable


__all__ = [Callable]
