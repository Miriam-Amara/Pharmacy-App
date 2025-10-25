#!/usr/bin/env python3

"""
Utility functions and database helpers.
"""

from flask import abort
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from typing import Type, TypeVar, Any
import logging

from models import storage
from models.basemodel import BaseModel
from models.employee import Employee


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


def check_email_username_exists(data: dict[str, Any]) -> None:
    """
    """
    if "email" in data:
        employee = Employee.search_employee_by_email_username(
            data["email"]
        )
        if employee:
            abort(409, description="Email already exist.")
    
    if "username" in data:
        employee = Employee.search_employee_by_email_username(
            data["username"]
        )
        if employee:
            abort(409, description="Username already exists.")

def get_obj(cls: Type[T], id: str) -> T | None:
    """
    Fetch a record by ID.
    """

    if not issubclass(cls, BaseModel):  # type: ignore
        abort(400, description="Invalid class")
    if not isinstance(id, str):  # type: ignore
        abort(400, description="id must be a valid string.")

    obj = storage.get_obj_by_id(cls, id)
    return obj


class DatabaseOp:
    """
    imple wrapper for database operations.
    """

    def save(self, obj: BaseModel):
        """
        Save object to database.
        """
        try:
            obj.save()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                detail = e.orig.diag.message_detail
                abort(409, description=detail)
            else:
                logger.error(f"Database operation failed: {e}")
                abort(500)
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            abort(500)

    def commit(self):
        """
        Commit all changes.
        """
        try:
            storage.save()
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            abort(500)

    def delete(self, obj: BaseModel):
        """
        Delete object from database.
        """
        try:
            obj.delete()
        except Exception as e:
            logger.error(f"{e}")
            abort(400, description="Database operation failed.")
