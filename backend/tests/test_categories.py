#!/usr/bin/env python3

"""
Unit tests for the Category API endpoints.
"""

from flask import Flask
from flask.testing import FlaskClient
from typing import Any
import logging
import unittest

from api.v1.app import create_app
from models.employee import Employee
from models.category import Category


logger = logging.getLogger(__name__)


class TestCategory(unittest.TestCase):
    """
    Tests the Category CRUD and authentication endpoints.

    POST - "/api/v1/categories"
    GET - "/api/v1/categories/<int:page_size>/<int:page_num>"
    GET - "/api/v1/categories/<category_id>"
    PUT - "/api/v1/categories/<category_id>"
    DELETE - "/api/v1/categories/<category_id>"
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Sets up the test app and logs in an admin user.
        """
        cls.app: Flask = create_app()
        cls.client: FlaskClient = cls.app.test_client()

        cls.employee_data: dict[str, Any] = {
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
            json=cls.employee_data,
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
        Registers a new category before each test.
        """
        self.category_data: dict[str, Any] = {
            "name": "antibiotics",
        }
        self.response = self.client.post(
            "/api/v1/categories",
            json=self.category_data,
        )
        self.category_id = self.response.get_json().get("id")

    def tearDown(self) -> None:
        """
        Deletes the category created for each test.
        """
        from api.v1.utils.utility import get_obj, DatabaseOp

        db = DatabaseOp()

        category = get_obj(Category, self.category_id)
        if not category:
            raise ValueError("Category not found")
        category.delete()
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
            raise ValueError("employee not found")
        employee.delete()
        db.commit()

    def test_register_categories(self):
        """
        Tests successful category registration.
        """
        self.assertEqual(self.response.status_code, 201)
        self.assertIn("name", self.response.get_json())
        self.assertNotIn("products", self.response.get_json())
        self.assertEqual(
            self.employee_data["username"].lower(),
            self.response.get_json().get("added_by"),
        )

    def test_get_all_categories(self):
        """
        Tests retrieval of all categories with pagination.
        """
        response = self.client.get("/api/v1/categories/5/1")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.get_json()), 5)

    def test_get_category(self):
        """
        Tests retrieval of a single category by ID.
        """
        response = self.client.get(f"/api/v1/categories/{self.category_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("name"),
            self.category_data["name"].lower(),
        )

    def test_update_category(self):
        """
        Tests updating category details.
        """
        new_data: dict[str, Any] = {
            "description": "Antibiotics for bacterial and viral infections."
        }
        response = self.client.put(
            f"/api/v1/categories/{self.category_id}", json=new_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("name"),
            self.category_data["name"].lower()
        )
        self.assertEqual(
            response.get_json().get("description"),
            new_data["description"].lower()
        )

    def test_delete_category(self):
        """
        Tests deleting a category record.
        """
        from api.v1.utils.utility import get_obj

        category_data: dict[str, Any] = {
            "name": "painkillers",
        }
        register_response = self.client.post(
            "/api/v1/categories",
            json=category_data,
        )
        category_id = register_response.get_json().get("id")

        delete_response = self.client.delete(
            f"/api/v1/categories/{category_id}"
        )
        self.assertEqual(delete_response.status_code, 200)

        category = get_obj(Category, category_id)
        self.assertIsNone(category)


if __name__ == "__main__":
    unittest.main(verbosity=2)
