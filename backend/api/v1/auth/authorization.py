#!/usr/bin/env python3

"""
Decorator for admin-only routes.
"""
from flask import g, abort
from typing import Callable, Any, TypeVar, cast
import functools
import logging


logger = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


def admin_only(func: F) -> F:
    """Allow only admin employees to access a route."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Check if current user is admin before running the function.
        """
        employee = getattr(g, "current_employee", None)
        if not employee:
            abort(401)
        employee = g.current_employee
        if not employee.is_admin:
            abort(403)
        return func(*args, **kwargs)

    return cast(F, wrapper)
