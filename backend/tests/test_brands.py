#!/usr/bin/env python3

"""
"""

from flask import Flask
from flask.testing import FlaskClient
import unittest

from api.v1.app import create_app


class TestBrand(unittest.TestCase):
    """
    POST - "/brands"
    GET - "/brands/<int:page_size>/<int:page_num>"
    GET - "brands/<brand_id>"
    PUT - "brands/<brand_id>"
    DELETE - "brands/<brand_id>"
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        """
        cls.app: Flask = create_app()
        cls.client: FlaskClient = cls.app.test_client()

        brand_data = {
            
        }


if __name__ == "__main__":
    unittest.main(verbosity=2)
