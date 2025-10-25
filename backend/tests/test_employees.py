#!/usr/bin/env python3

"""
Unit tests for the Employee API endpoints.
"""

from flask import Flask
from flask.testing import FlaskClient
from typing import Any
import logging
import unittest

from api.v1.app import create_app
from models.employee import Employee


logger = logging.getLogger(__name__)


class TestEmployee(unittest.TestCase):
    """
    Tests the Employee CRUD and authentication endpoints.

    POST - "/api/v1/register"
    GET - "/api/v1/employees/<int:page_size>/<int:page_num>"
    GET - "/api/v1/employees/<employee_id>"
    PUT - "/api/v1/employees/<employee_id>"
    DELETE - "/api/v1/employees/<employee_id>"
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Sets up the test app and logs in an admin user.
        """
        cls.app: Flask = create_app()
        cls.client: FlaskClient = cls.app.test_client()

        employee_data: dict[str, Any] = {
            "first_name": "Range",
            "last_name": "Rover",
            "username": "RRover",
            "email": "rangerover@gmail.com",
            "password": "Ranger1234",
            "home_address": "No. 1 sporty street",
            "role": "Manager",
            "is_admin": True,
        }

        cls.client.post(
            "/api/v1/register",
            json=employee_data,
        )
        response = cls.client.post(
            "/api/v1/auth_session/login",
            json={"username": "RRover", "password": "Ranger1234"},
        )
        cls.employee_id = response.get_json().get("employee_id")

        session_cookie = response.headers.get("Set-Cookie")
        if session_cookie:
            cookie_name, session_id = (
                session_cookie.split(";", 1)[0].split("=", 1)
            )
            cls.client.set_cookie(cookie_name, session_id)

    def setUp(self) -> None:
        """
        Registers a new employee before each test.
        """
        self.employee_data: dict[str, Any] = {
            "first_name": "Ferry",
            "last_name": "Wheels",
            "username": "FWheels",
            "email": "ferrywheels@gmail.com",
            "password": "Ferry1234",
            "home_address": "No. 50 Okwu street",
            "role": "salesperson",
        }
        self.response = self.client.post(
            "/api/v1/register",
            json=self.employee_data,
        )
        self.employee_id = self.response.get_json().get("id")

    def tearDown(self) -> None:
        """
        Deletes the employee created for each test.
        """
        from api.v1.utils.utility import get_obj, DatabaseOp

        db = DatabaseOp()

        employee = get_obj(Employee, self.employee_id)
        if not employee:
            raise ValueError("Employee not found")
        employee.delete()
        db.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Deletes the admin user created for the test class.
        """
        from api.v1.utils.utility import get_obj, DatabaseOp

        db = DatabaseOp()

        employee = get_obj(Employee, cls.employee_id)
        if not employee:
            raise ValueError("Employee not found")
        employee.delete()
        db.commit()

    def test_register_employees(self):
        """
        Tests successful employee registration.
        """

        self.assertEqual(self.response.status_code, 201)
        self.assertNotIn("employee_session", self.response.get_json())

    def test_get_all_employees(self):
        """
        Tests retrieval of all employees with pagination.
        """
        response = self.client.get("/api/v1/employees/5/1")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.get_json()), 5)

    def test_get_employee(self):
        """
        Tests retrieval of a single employee by ID.
        """
        response = self.client.get(
            f"/api/v1/employees/{self.employee_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("first_name"),
            self.employee_data["first_name"].lower(),
        )

    def test_update_employee(self):
        """
        Tests updating employee details.
        """
        new_data = {
            "first_name": "Bentley",
            "middle_name": "horn",
            "username": "newusername",
            "email": "newemail@gmail.com",
        }
        response = self.client.put(
            f"/api/v1/employees/{self.employee_id}",
            json=new_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("first_name"),
            new_data["first_name"].lower()
        )
        self.assertNotEqual(
            response.get_json().get("username"),
            new_data["username"].lower()
        )
        self.assertNotEqual(
            response.get_json().get("email"),
            new_data["email"].lower()
        )

    def test_delete_employee(self):
        """
        Tests deleting an employee record.
        """
        from api.v1.utils.utility import get_obj

        employee_data: dict[str, Any] = {
            "first_name": "Helen",
            "last_name": "Adamma",
            "username": "AHelen",
            "email": "helen@gmail.com",
            "password": "Helen467",
            "home_address": "No. 4 darling street",
            "role": "salesperson",
        }
        register_response = self.client.post(
            "/api/v1/register",
            json=employee_data,
        )
        employee_id = register_response.get_json().get("id")

        delete_response = self.client.delete(
            f"/api/v1/employees/{employee_id}"
        )
        self.assertEqual(delete_response.status_code, 200)

        employee = get_obj(Employee, employee_id)
        self.assertIsNone(employee)


if __name__ == "__main__":
    unittest.main(verbosity=2)
