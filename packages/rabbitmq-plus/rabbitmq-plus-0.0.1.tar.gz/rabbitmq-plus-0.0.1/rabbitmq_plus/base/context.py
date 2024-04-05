# -*- coding: utf-8 -*-
from flask import current_app
from typing import Any, Callable


def is_current_app() -> Any:
    try:
        with current_app.app_context():
            return True
    except RuntimeError:
        return False


def is_callable(handle: Callable) -> bool:
    """Returns a bool value if the handle passed in is a callable
    method/function

    :param any handle: The object to check
    :rtype: bool

    """
    return isinstance(handle, Callable)
