#!/usr/bin/env python3

"""
Unit tests for the PurchaseOrderItem API endpoints.
"""

from flask import Flask
from flask.testing import FlaskClient
from typing import Any
import logging
import unittest

from api.v1.app import create_app
from models import storage
from models.brand import Brand
from models.employee import Employee
from models.product import Product
from models.purchase_order import PurchaseOrder


logger = logging.getLogger(__name__)


class TestPurchase_order_item(unittest.TestCase):
    """
    Tests the PurchaseOrderItem CRUD and authentication endpoints.

    POST - "/api/v1/purchase_orders/<purchase_order_id>/purchase_order_items"
    GET - "/api/v1/purchases/<int:page_size>/<int:page_num>"
    GET - "/api/v1/purchase_orders/<order_id>/purchase_order_items/<order_item_id>"
    PUT - "/api/v1/purchase_orders/<order_id>/purchase_order_items/<order_item_id>"
    DELETE - "/api/v1/purchase_orders/<order_id>/purchase_order_items/<order_item_id>"
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

    def add_product(self) -> None:
        """
        """
        self.product_data: dict[str, Any] = {
            "name": "Paracetamol",
            "selling_price": 350,
        }
        response = self.client.post(
            "/api/v1/products",
            json=self.product_data,
        )
        self.product_id = response.get_json().get("id")

    def delete_product(self) -> None:
        """
        """
        product: Product | None = storage.get_obj_by_id(
            Product, self.product_id
        )
        if not product:
            raise ValueError("Product not found")
  
        storage.delete(product)
        storage.save()

    def add_brand(self) -> None:
        """
        """
        self.brand_data = {"name": "Emzor"}
        brand_response = self.client.post(
            "/api/v1/brands",
            json=self.brand_data,
        )
        self.brand_id: str = brand_response.get_json().get("id")
    
    def delete_brand(self) -> None:
        """
        """
        brand: Brand | None = storage.get_obj_by_id(Brand, self.brand_id)
        if not brand:
            raise ValueError("Brand not found")
        
        storage.delete(brand)
        storage.save()

    def add_purchase_order(self) -> None:
        """
        """
        self.order_data = {"brand_id": self.brand_id}
        response = self.client.post(
            "/api/v1/purchase_orders",
            json=self.order_data,
        )
        self.order_id: str = response.get_json().get("id")

    def delete_purchase_order(self) -> None:
        """
        """
        order: PurchaseOrder | None = storage.get_obj_by_id(
            PurchaseOrder, self.order_id
        )
        if not order:
            raise ValueError("Order not found")
        
        storage.delete(order)
        storage.save()

    def setUp(self) -> None:
        """
        Registers a new purchase_order_item before each test.
        """
        self.add_brand()
        self.add_product()
        self.add_purchase_order()

        self.order_item_data: dict[str, Any] = {
            "product_id": self.product_id,
            "quantity": 2,
            "unit_cost_price": 200,
            "total_cost_price": 400,
            "payment_status": "paid",
        }
        self.response = self.client.post(
            f"/api/v1/purchase_orders/{self.order_id}/purchase_order_items",
            json=self.order_item_data,
        )
        self.order_item_id = self.response.get_json().get("id")

    def tearDown(self) -> None:
        """
        Deletes the purchase_order_item created for each test.
        """
        self.client.delete(
            f"/api/v1/purchase_orders/{self.order_id}"
            f"/purchase_order_items/{self.order_item_id}",
        )
        self.delete_brand()
        self.delete_product()
        self.delete_purchase_order()

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

    def test_register_purchase_order_items(self):
        """
        Tests successful purchase_order_item registration.
        """
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(
            self.response.get_json().get("purchase_order_id"),
            self.order_id
        )
        self.assertEqual(
            self.response.get_json().get("product_id"),
            self.product_id
        )
        self.assertEqual(
            self.response.get_json().get("quantity"),
            self.order_item_data["quantity"]
        )
        self.assertEqual(
            self.response.get_json().get("unit_cost_price"),
            self.order_item_data["unit_cost_price"]
        )
        self.assertEqual(
            self.response.get_json().get("total_cost_price"),
            self.order_item_data["total_cost_price"]
        )
        self.assertEqual(
            self.response.get_json().get("payment_status"),
            self.order_item_data["payment_status"].lower()
        )
        self.assertEqual(
            self.response.get_json().get("product"),
            self.product_data["name"].lower()
        )
        self.assertIn("item_status", self.response.get_json())
        self.assertEqual(len(self.response.get_json()), 12)

    
    def test_get_all_purchase_order_items(self):
        """
        Tests retrieval of all purchase_order_items with pagination.
        """
        response = self.client.get("/api/v1/purchases/5/1")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.get_json()), 5)

    def test_get_purchase_order_item(self):
        """
        Tests retrieval of a single purchase_order_item by ID.
        """
        response = self.client.get(
            f"/api/v1/purchase_orders/{self.order_id}"
            f"/purchase_order_items/{self.order_item_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.response.get_json().get("purchase_order_id"),
            self.order_id
        )
        self.assertEqual(
            self.response.get_json().get("product_id"),
            self.product_id
        )
        self.assertEqual(
            self.response.get_json().get("quantity"),
            self.order_item_data["quantity"]
        )
        self.assertEqual(
            self.response.get_json().get("unit_cost_price"),
            self.order_item_data["unit_cost_price"]
        )
        self.assertEqual(
            self.response.get_json().get("total_cost_price"),
            self.order_item_data["total_cost_price"]
        )
        self.assertEqual(
            self.response.get_json().get("payment_status"),
            self.order_item_data["payment_status"].lower()
        )
        self.assertEqual(
            self.response.get_json().get("product"),
            self.product_data["name"].lower()
        )
        self.assertIn("item_status", self.response.get_json())
        self.assertEqual(len(self.response.get_json()), 12)

    def test_update_purchase_order_item(self):
        """
        Tests updating purchase_order_item details.
        """
        new_data: dict[str, Any] = {
            "quantity": 4,
            "total_cost_price": 4 * self.order_item_data["unit_cost_price"]
        }
        response = self.client.put(
            f"/api/v1/purchase_orders/{self.order_id}"
            f"/purchase_order_items/{self.order_item_id}",
            json=new_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("quantity"),
            new_data["quantity"]
        )
        self.assertEqual(
            response.get_json().get("total_cost_price"),
            new_data["total_cost_price"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
