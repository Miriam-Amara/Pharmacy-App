#!/usr/bin/env python3

"""
Unit tests for the Sale API endpoints.
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


logger = logging.getLogger(__name__)


class TestSale(unittest.TestCase):
    """
    Tests the Sale CRUD and authentication endpoints.

    POST - "/api/v1/sales"
    GET - "/api/v1/sales/<int:page_size>/<int:page_num>"
    GET - "/api/v1/sales/<sale_id>"
    PUT - "/api/v1/sales/<sale_id>"
    DELETE - "/api/v1/sales/<sale_id>"
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


    def setUp(self) -> None:
        """
        Registers a new sale before each test.
        """
        self.add_brand()
        self.add_product()

        quantity = 50
        unit_cost = 200
        self.sale_item_data: dict[str, Any] = {
            "brand_id": self.brand_id,
            "product_id": self.product_id,
            "quantity": quantity,
            "unit_selling_price": unit_cost,
            "total_selling_price": quantity * unit_cost,
        }
        self.response = self.client.post(
            "/api/v1/sales",
            json=self.sale_item_data,
        )
        self.sale_id = self.response.get_json().get("id")

    def tearDown(self) -> None:
        """
        Deletes the sale created for each test.
        """
        self.client.delete(f"/api/v1/sales/{self.sale_id}")
        self.delete_brand()
        self.delete_product()

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

    def test_register_sales(self):
        """
        Tests successful sale registration.
        """
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(
            self.response.get_json().get("brand_id"),
            self.brand_id
        )
        self.assertEqual(
            self.response.get_json().get("product_id"),
            self.product_id
        )
        self.assertEqual(
            self.response.get_json().get("quantity"),
            self.sale_item_data["quantity"]
        )
        self.assertEqual(
            self.response.get_json().get("unit_selling_price"),
            self.sale_item_data["unit_selling_price"]
        )
        self.assertEqual(
            self.response.get_json().get("total_selling_price"),
            self.sale_item_data["total_selling_price"]
        )
        self.assertEqual(
            self.response.get_json().get("brand"),
            self.brand_data["name"].lower()
        )
        self.assertEqual(
            self.response.get_json().get("product"),
            self.product_data["name"].lower()
        )
        self.assertEqual(
            self.response.get_json().get("added_by"),
            self.employee_data["username"].lower()
        )
        self.assertEqual(len(self.response.get_json()), 13)

    
    def test_get_all_sales(self):
        """
        Tests retrieval of all sales with pagination.
        """
        response = self.client.get("/api/v1/sales/5/1")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.get_json()), 5)

    def test_get_sale(self):
        """
        Tests retrieval of a single sale by ID.
        """
        response = self.client.get(f"/api/v1/sales/{self.sale_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.response.get_json().get("brand_id"),
            self.brand_id
        )
        self.assertEqual(
            self.response.get_json().get("product_id"),
            self.product_id
        )
        self.assertEqual(
            self.response.get_json().get("quantity"),
            self.sale_item_data["quantity"]
        )
        self.assertEqual(
            self.response.get_json().get("unit_selling_price"),
            self.sale_item_data["unit_selling_price"]
        )
        self.assertEqual(
            self.response.get_json().get("total_selling_price"),
            self.sale_item_data["total_selling_price"]
        )
        self.assertEqual(
            self.response.get_json().get("brand"),
            self.brand_data["name"].lower()
        )
        self.assertEqual(
            self.response.get_json().get("product"),
            self.product_data["name"].lower()
        )
        self.assertEqual(
            self.response.get_json().get("added_by"),
            self.employee_data["username"].lower()
        )
        self.assertEqual(len(self.response.get_json()), 13)

    def test_update_sale(self):
        """
        Tests updating sale details.
        """
        new_data: dict[str, Any] = {
            "quantity": 4,
            "total_selling_price": 4 * self.sale_item_data["unit_selling_price"]
        }
        response = self.client.put(
            f"/api/v1/sales/{self.sale_id}",
            json=new_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json().get("quantity"),
            new_data["quantity"]
        )
        self.assertEqual(
            response.get_json().get("total_selling_price"),
            new_data["total_selling_price"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
