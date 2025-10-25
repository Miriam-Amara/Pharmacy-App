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
from models import storage
from models.employee import Employee
from models.brand import Brand
from models.product import Product


logger = logging.getLogger(__name__)


class TestBrand(unittest.TestCase):
    """
    Tests the Brand CRUD and authentication endpoints.

    POST - "/api/v1/products/<product_id>/brands/<brand_id>"
    GET - "/api/v1/products/<product_id>/brands"
    GET - "/api/v1/brands/<brand_id>/products"
    DELETE - "/api/v1/products/<product_id>/brands/<brand_id>"
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
        Registers new brands and new products before each test.
        """
        self.brands: list[dict[str, str]] = [
            {"name": "Emzor"},
            {"name": "M&B"},
            {"name": "Fidson"},
            {"name": "Pharma-Deko"},
            {"name": "Swiss Pharma"},
        ]
        self.products: list[dict[str, Any]] = [
            {"name": "Paracetamol", "selling_price": 350},
            {"name": "Panadol", "selling_price": 500},
            {"name": "Lumartem", "selling_price": 1000},
            {"name": "Panadol Extra", "selling_price": 600},
            {"name": "Ibuprofen", "selling_price": 700},
        ]
        self.brand_ids: list[str] = []
        self.product_ids: list[str] = []

        for brand_data in self.brands:
            response = self.client.post(
                "/api/v1/brands",
                json=brand_data,
            )
            self.brand_ids.append(response.get_json().get("id"))

        for product_data in self.products:
            response = self.client.post(
                "/api/v1/products",
                json=product_data,
            )
            self.product_ids.append(response.get_json().get("id"))

    def tearDown(self) -> None:
        """
        Deletes the brands and products created for each test.
        """
        for brand_id in self.brand_ids:
            brand: Brand | None = storage.get_obj_by_id(Brand, brand_id)
            if not brand:
                raise ValueError("Brand not found")
            storage.delete(brand)

        for product_id in self.product_ids:
            product: Product | None = storage.get_obj_by_id(
                Product, product_id
            )
            if not product:
                raise ValueError("Product not found")
            storage.delete(product)

        storage.save()

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

    def test_add_product_brands(self):
        """ """
        for product_id in self.product_ids:
            for brand_id in self.brand_ids:
                response = self.client.post(
                    f"/api/v1/products/{product_id}/brands/{brand_id}"
                )
                self.assertEqual(response.status_code, 201)

    def test_get_product_brands(self):
        """ """
        # add product brands
        for product_id in self.product_ids:
            for brand_id in self.brand_ids:
                self.client.post(
                    f"/api/v1/products/{product_id}/brands/{brand_id}"
                )

        # get product brands
        response = self.client.get(
            f"/api/v1/products/{self.product_ids[0]}/brands"
        )
        self.assertEqual(
            response.get_json().get("product_name"),
            self.products[0]["name"].lower()
        )

        product_brands = response.get_json().get("brands")
        for brand in self.brands:
            self.assertIn(brand["name"].lower(), product_brands)

    def test_get_brand_products(self):
        """ """
        # add product brands
        for product_id in self.product_ids:
            for brand_id in self.brand_ids:
                self.client.post(
                    f"/api/v1/products/{product_id}/brands/{brand_id}"
                )

        # get a brand products
        response = self.client.get(
            f"/api/v1/brands/{self.brand_ids[0]}/products"
        )
        self.assertEqual(
            response.get_json().get("brand_name"),
            self.brands[0]["name"].lower()
        )

        brand_products = response.get_json().get("products")
        for product in self.products:
            self.assertIn(product["name"].lower(), brand_products)

    def test_delete_product_brand(self):
        """ """
        # add product brands
        for product_id in self.product_ids:
            for brand_id in self.brand_ids:
                self.client.post(
                    f"/api/v1/products/{product_id}/brands/{brand_id}"
                )

        for brand_id in self.brand_ids:
            response = self.client.delete(
                f"/api/v1/products/{self.product_ids[0]}/brands/{brand_id}"
            )
            self.assertEqual(response.status_code, 200)

        product: Product | None = storage.get_obj_by_id(
            Product, self.product_ids[0]
        )
        if not product:
            raise ValueError("Product not found")
        self.assertEqual([], product.brands)


if __name__ == "__main__":
    unittest.main(verbosity=2)
