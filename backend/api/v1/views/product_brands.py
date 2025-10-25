#!/usr/bin/env python3

"""
Brand routes for managing product-brand relationships.
"""

from flask import abort, jsonify
from typing import Any

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.utility import get_obj
from models.product import Product
from models.brand import Brand


def all_brand_products(brand: Brand) -> dict[str, Any]:
    """
    Return brand data excluding relations.
    """
    product_list: list[str] = [
        product.name for product in brand.products
    ]
    brand_products: dict[str, Any] = {
        "brand_name": brand.name,
        "products": product_list
    }
    return brand_products


def all_product_brands(product: Product) -> dict[str, Any]:
    """
    Return brand data excluding relations.
    """
    brand_list: list[str] = [
        brand.name for brand in product.brands
    ]
    product_brands: dict[str, Any] = {
        "product_name": product.name,
        "brands": brand_list
    }
    return product_brands


@app_views.route(
    "products/<product_id>/brands/<brand_id>",
    strict_slashes=False,
    methods=["POST"]
)
@admin_only
def add_product_brands(product_id: str, brand_id: str):
    """
    Link a brand to a product.
    """
    product = get_obj(Product, product_id)
    if not product:
        abort(404, description="Product does not exist")

    brand = get_obj(Brand, brand_id)
    if not brand:
        abort(404, description="Brand does not exist")

    product.brands.append(brand)
    product.save()

    product_brands = all_product_brands(product)
    return jsonify(product_brands), 201


@app_views.route(
        "products/<product_id>/brands",
        strict_slashes=False,
        methods=["GET"]
    )
@admin_only
def get_product_brands(product_id: str):
    """
    "Get all brands linked to a product.
    """
    product = get_obj(Product, product_id)
    if not product:
        abort(404, description="Product does not exist")

    product_brands = all_product_brands(product)
    return jsonify(product_brands), 200


@app_views.route(
        "brands/<brand_id>/products",
        strict_slashes=False,
        methods=["GET"]
    )
@admin_only
def get_brand_products(brand_id: str):
    """
    "Get all products linked to a brand.
    """
    brand = get_obj(Brand, brand_id)
    if not brand:
        abort(404, description="Brand does not exist")

    brand_products = all_brand_products(brand)
    return jsonify(brand_products), 200


@app_views.route(
    "products/<product_id>/brands/<brand_id>",
    strict_slashes=False,
    methods=["DELETE"]
)
@admin_only
def delete_product_brand(product_id: str, brand_id: str):
    """
    Unlink a brand from a product.
    """
    product = get_obj(Product, product_id)
    if not product:
        abort(404, description="Product does not exist")

    brand = get_obj(Brand, brand_id)
    if not brand:
        abort(404, description="Brand does not exist")

    product.brands.remove(brand)
    product.save()
    return jsonify({}), 200
