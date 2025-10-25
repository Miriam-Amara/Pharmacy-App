#!/usr/bin/env python3

"""
Unit tests for the Brand API endpoints.
"""

from flask import Flask
from flask.testing import FlaskClient
from typing import Any
import logging
import unittest

from api.v1.app import create_app
from models.employee import Employee
from models.brand import Brand


logger = logging.getLogger(__name__)


class TestBrand(unittest.TestCase):
    """
    Tests the Brand CRUD and authentication endpoints.

    POST - "/api/v1/brands"
    GET - "/api/v1/brands/<int:page_size>/<int:page_num>"
    GET - "/api/v1/brands/<brand_id>"
    PUT - "/api/v1/brands/<brand_id>"
    DELETE - "/api/v1/brands/<brand_id>"
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
                session_cookie
                .split(";", 1)[0]
                .split("=", 1)
            )
            cls.client.set_cookie(cookie_name, session_id)

    def setUp(self) -> None:
        """
        Registers a new brand before each test.
        """
        self.brand_data: dict[str, Any] = {
            "name": "Emzor",
        }
        self.response = self.client.post(
            "/api/v1/brands",
            json=self.brand_data,
        )
        self.brand_id = self.response.get_json().get("id")

    def tearDown(self) -> None:
        """
        Deletes the brand created for each test.
        """
        from api.v1.utils.utility import get_obj, DatabaseOp

        db = DatabaseOp()

        brand = get_obj(Brand, self.brand_id)
        if not brand:
            raise ValueError("Brand not found")
        brand.delete()
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

    def test_register_brands(self):
        """
        Tests successful brand registration.
        """
        self.assertEqual(self.response.status_code, 201)
        self.assertIn("name", self.response.get_json())
        self.assertIn("is_active", self.response.get_json())
        self.assertEqual(
            self.employee_data["username"].lower(),
            self.response.get_json().get("added_by")
        )

    def test_get_all_brands(self):
        """
        Tests retrieval of all brands with pagination.
        """
        response = self.client.get("/api/v1/brands/5/1")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.get_json()), 5)

    def test_get_brand(self):
        """
        Tests retrieval of a single brand by ID.
        """
        response = self.client.get(
            f"/api/v1/brands/{self.brand_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("name"),
            self.brand_data["name"].lower(),
        )

    def test_update_brand(self):
        """
        Tests updating brand details.
        """
        new_data: dict[str, Any] = {"name": "M&D", "is_active": False}
        response = self.client.put(
            f"/api/v1/brands/{self.brand_id}", json=new_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("name"),
            new_data["name"].lower()
        )
        self.assertEqual(
            response.get_json().get("is_active"),
            new_data["is_active"]
        )

    def test_delete_brand(self):
        """
        Tests deleting a brand record.
        """
        from api.v1.utils.utility import get_obj

        brand_data: dict[str, Any] = {
            "name": "Arthemater",
        }
        register_response = self.client.post(
            "/api/v1/brands",
            json=brand_data,
        )
        brand_id = register_response.get_json().get("id")

        delete_response = self.client.delete(
            f"/api/v1/brands/{brand_id}"
        )
        self.assertEqual(delete_response.status_code, 200)

        brand = get_obj(Brand, brand_id)
        self.assertIsNone(brand)


if __name__ == "__main__":
    unittest.main(verbosity=2)
