#!/usr/bin/env python3

"""
Utility functions and database helpers.
"""

from flask import abort
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from typing import Type, TypeVar
import logging

from models import storage
from models.basemodel import BaseModel


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


def get_obj(cls: Type[T], id: str) -> T | None:
    """
    Fetch a record by ID.
    """

    if not issubclass(cls, BaseModel):  # type: ignore
        logger.error("Invalid class")
        abort(400)
    if not isinstance(id, str):  # type: ignore
        logger.error("id must be a valid string")
        abort(400)

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
