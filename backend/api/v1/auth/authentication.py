#!/usr/env python3

"""
Provides base and login authentication logic for employees.

This module defines:
- BaseAuth: Handles generic authentication utilities
            (session cookies, path checks).
- LoginAuth: Handles employee login validation,
             authentication, and session management.
"""


from dotenv import load_dotenv
from flask import request, abort
from typing import cast
import logging
import os

from api.v1.utils.request_data_validation import (
    EmployeeLogin,
    get_request_data,
    validate_request_data,
)
from models.employee import Employee


load_dotenv()
logger = logging.getLogger(__name__)


class BaseAuth:
    """
    Provides foundational authentication utilities such as:
    - Path-based access control.
    - Retrieving session cookies.
    """

    def require_auth(self, path: str, excluded_paths: list[str]) -> bool:
        """
        Determines if a request path requires authentication.

        Args:
            path (str): The request path.
            excluded_paths (list[str]): List of paths that are
                                        publicly accessible.

        Returns:
            bool: True if authentication is required, False otherwise.
        """
        if not path or not excluded_paths:
            return True
        if not path.endswith("/"):
            path += "/"
        if path in excluded_paths:
            return False
        return True

    def session_cookie(self) -> str | None:
        """
        Retrieves the session cookie from the incoming request.

        Returns:
            str | None: The session cookie value, or None if not found.
        """
        cookie_name = os.getenv("SESSION_NAME")
        if not cookie_name:
            logger.error("SESSION_NAME environment variable not set")
            return
        return request.cookies.get(cookie_name)

    def current_employee(self) -> Employee | None:
        """
        Returns the currently authenticated employee, if any.

        To be implemented by the subclass handling
        specific authentication methods.
        """
        pass


class LoginAuth:
    """
    Handles employee login logic:
    - Validates login request data.
    - Authenticates user credentials.
    - Creates or retrieves session data.
    """

    def __init__(self) -> None:
        """
        Initializes the LoginAuth instance and
        verifies the session cookie name.
        """
        self.cookie_name = os.getenv("SESSION_NAME")
        if not self.cookie_name:
            logger.error("SESSION_NAME environment variable not set")
            abort(500)

    def validate_login_request_data(self) -> dict[str, str]:
        """
        Validates and extracts login credentials from the request data.

        Returns:
            dict[str, str]: The validated login data
                            (email/username and password).

        Raises:
            400: If neither email nor username is provided.
        """
        email = get_request_data().get("email")
        username = get_request_data().get("username")

        if not any([email, username]):
            abort(400, description="Must have either email or username")

        valid_data = validate_request_data(EmployeeLogin)

        return valid_data

    def authenticate_employee(
        self, email: str | None, username: str | None, password: str | None
    ) -> Employee:
        """Authenticate a user by email or username and password."""
        from api.v1.app import bcrypt

        if not email and not username:
            abort(400, description="Either email or username is required")
        if not password:
            abort(400, description="Password required")

        employee = Employee.search_employee_by_email_username(email, username)
        if not employee:
            abort(404, description="No employee found")

        if not bcrypt.check_password_hash(  # type: ignore
            employee.password, password
        ):
            abort(401, description="wrong password")

        return employee

    def create_employee_session(
            self,
            employee: Employee
    ) -> tuple[str, str]:
        """
        Creates a new session for the given employee.
        """
        from api.v1.app import auth

        session_id = auth.create_session(employee.id)
        if not session_id:
            logger.error("No session id found")
            abort(500)

        return cast(str, self.cookie_name), session_id

    def get_employee_session(
            self,
            employee: Employee
    ) -> tuple[str, str] | None:
        """
        Retrieves an existing session for the given employee, if any.
        """
        from api.v1.app import auth

        session_id = auth.get_session(employee)
        if not session_id:
            return

        return cast(str, self.cookie_name), session_id

    def login_employee(self) -> tuple[str, str, str]:
        """
        Handles the full employee login process:
            - Validates request data.
            - Authenticates credentials.
            - Reuses or creates a session.

        Returns:
            tuple[str, str, str]: (cookie_name, session_id, employee_id)
        """
        valid_request_data = self.validate_login_request_data()
        email = valid_request_data.get("email")
        username = valid_request_data.get("username")
        password = valid_request_data.get("password")

        employee = self.authenticate_employee(email, username, password)

        existing_session = self.get_employee_session(employee)
        if existing_session:
            cookie, session_id = existing_session
        else:
            cookie, session_id = self.create_employee_session(employee)

        return cookie, session_id, employee.id
