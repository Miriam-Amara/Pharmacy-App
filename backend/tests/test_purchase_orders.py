#!/usr/bin/env python3

"""
Unit tests for the PurchaseOrder API endpoints.
"""

from flask import Flask
from flask.testing import FlaskClient
from typing import Any
import logging
import unittest

from api.v1.app import create_app
from models.employee import Employee
from models.brand import Brand
from models.purchase_order import PurchaseOrder


logger = logging.getLogger(__name__)


class TestOrder(unittest.TestCase):
    """
    Tests the Order CRUD and authentication endpoints.

    POST - "/api/v1/purchase_orders"
    GET - "/api/v1/purchase_orders/<int:page_size>/<int:page_num>"
    GET - "/api/v1/purchase_orders/<order_id>"
    PUT - "/api/v1/purchase_orders/<order_id>"
    DELETE - "/api/v1/purchase_orders/<order_id>"
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
        Creates a new purchase order before each test.
        """
        # create brand
        self.brand_data: dict[str, Any] = {
            "name": "Emzor",
        }
        self.brand_response = self.client.post(
            "/api/v1/brands",
            json=self.brand_data,
        )
        self.brand_id: str = self.brand_response.get_json().get("id")

        # creete purchase order
        self.order_data: dict[str, str] = {"brand_id": self.brand_id}
        self.response = self.client.post(
            "/api/v1/purchase_orders",
            json=self.order_data,
        )
        self.order_id = self.response.get_json().get("id")

    def tearDown(self) -> None:
        """
        Deletes the purchase order created for each test.
        """
        from api.v1.utils.utility import get_obj, DatabaseOp

        db = DatabaseOp()

        brand: Brand | None = get_obj(Brand, self.brand_id)
        order: PurchaseOrder | None = get_obj(
            PurchaseOrder, self.order_id
        )

        if not brand:
            raise ValueError("Brand not found.")
        if not order:
            raise ValueError("Order not found.")
        brand.delete()
        order.delete()
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

    def test_register_orders(self):
        """
        Tests successful purchase order registration.
        """
        self.assertEqual(self.response.status_code, 201)
        self.assertIn("status", self.response.get_json())
        self.assertIn("brand_id", self.response.get_json())
        self.assertIn("employee_id", self.response.get_json())
        self.assertEqual(
            self.response.get_json().get("brand"),
            self.brand_data["name"].lower()
        )
        self.assertEqual(
            self.response.get_json().get("added_by"),
            self.employee_data["username"].lower(),
        )
        self.assertEqual(len(self.response.get_json()), 9)

    def test_get_all_orders(self):
        """
        Tests retrieval of all orders with pagination.
        """
        response = self.client.get("/api/v1/purchase_orders/5/1")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.get_json()), 5)

    def test_get_order(self):
        """
        Tests retrieval of a single order by ID.
        """
        response = self.client.get(
            f"/api/v1/purchase_orders/{self.order_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.get_json())
        self.assertIn("brand_id", response.get_json())
        self.assertIn("employee_id", response.get_json())
        self.assertEqual(
            response.get_json().get("brand"),
            self.brand_data["name"].lower()
        )
        self.assertEqual(
            response.get_json().get("added_by"),
            self.employee_data["username"].lower()
        )
        self.assertEqual(len(response.get_json()), 9)

    def test_update_order(self):
        """
        Tests updating order details.
        """
        # create brand
        brand_data: dict[str, str] = {"name": "M&D"}
        brand_response = self.client.post(
            "/api/v1/brands",
            json=brand_data,
        )
        brand_id = brand_response.get_json().get("id")

        # update existing purchase order with the new brand id
        response = self.client.put(
            f"/api/v1/purchase_orders/{self.order_id}",
            json={"brand_id": brand_id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get("brand_id"), brand_id)
        self.assertEqual(
            response.get_json().get("brand"),
            brand_data["name"].lower()
        )

        # delete brand
        self.client.delete(f"/api/v1/brands/{brand_id}")

    def test_delete_order(self):
        """
        Tests deleting a purchase order record.
        """
        from api.v1.utils.utility import get_obj

        # add a new order
        register_order_response = self.client.post(
            "/api/v1/purchase_orders",
            json={"brand_id": self.brand_id, "status": "cancelled"},
        )
        order_id = register_order_response.get_json().get("id")

        # delete the new order
        delete_order_response = self.client.delete(
            f"/api/v1/purchase_orders/{order_id}"
        )
        self.assertEqual(delete_order_response.status_code, 200)

        order = get_obj(PurchaseOrder, order_id)
        self.assertIsNone(order)


if __name__ == "__main__":
    unittest.main(verbosity=2)
