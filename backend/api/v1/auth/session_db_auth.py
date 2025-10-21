#!/usr/bin/env python3

"""
Handles database-backed session authentication for employees.
"""

from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import abort
import logging
import os

from api.v1.utils.utility import get_obj
from api.v1.auth.authentication import BaseAuth
from models.employee import Employee
from models.employee_session import EmployeeSession


load_dotenv()
logger = logging.getLogger(__name__)


class SessionDBAuth(BaseAuth):
    """
    Manage user sessions using the database.
    """

    def __init__(self) -> None:
        """
        Initialize session duration from environment.
        """
        self.session_duration = int(os.getenv("SESSION_DURATION", 0))

    def create_session(self, employee_id: str | None = None) -> str | None:
        """
        Create and save a new session for an employee.
        """
        if not employee_id or not isinstance(employee_id, str):  # type: ignore
            return

        employee_session = EmployeeSession(employee_id=employee_id)
        try:
            employee_session.save()
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            abort(500)

        return employee_session.id

    def current_employee(self) -> Employee | None:
        """
        Return the employee linked to the current session cookie.
        """
        session_id = self.session_cookie()
        if not session_id:
            return

        employee_id = self.employee_id_for_session_id(session_id)
        if not employee_id:
            return

        employee = get_obj(Employee, employee_id)
        if employee:
            return employee

    def destroy_session(self) -> bool | None:
        """
        Delete the current session record.
        """
        session_id = self.session_cookie()
        if not session_id:
            return

        employee_session = get_obj(EmployeeSession, session_id)
        if not employee_session:
            return

        try:
            employee_session.delete()
            employee_session.save()
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            return
        return True

    def employee_id_for_session_id(
            self,
            session_id: str | None = None
    ) -> str | None:
        """
        Return employee ID for a valid session ID.
        """
        if not session_id or not isinstance(session_id, str):  # type: ignore
            return

        session = get_obj(EmployeeSession, session_id)
        if not session:
            return

        if (
            session.created_at + timedelta(seconds=self.session_duration)
            < datetime.now()
        ):
            try:
                session.delete()
                session.save()
            except Exception as e:
                logger.error(f"Failed to delete expired session: {e}")
            return
        return session.employee_id

    def get_session(self, employee: Employee) -> str | None:
        """
        Return a valid active session ID for the given employee.
        """
        if not employee.employee_session:
            return

        employee_session_obj = employee.employee_session[0]
        if (
            employee_session_obj.created_at
            + timedelta(seconds=self.session_duration)
            > datetime.now()
        ):
            return employee_session_obj.id
        return
