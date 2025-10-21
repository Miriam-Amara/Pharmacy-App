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


def get_brand_dict(brand: Brand) -> dict[str, Any]:
    """
    Return brand data excluding relations.
    """
    brand_dict: dict[str, Any] = {}
    brand_to_dict = brand.to_dict()
    excluded_attr = ["products", "sales", "purchase_orders", "added_by"]
    for attr, value in brand_to_dict.items():
        if attr in excluded_attr:
            continue
        else:
            brand_dict[attr] = value
    return brand_dict


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

    product_brands: list[dict[str, Any]] = []
    for brand in product.brands:
        brand_dict = get_brand_dict(brand)
        product_brands.append(brand_dict)
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

    product_brands: list[dict[str, Any]] = []
    for brand in product.brands:
        brand_dict = get_brand_dict(brand)
        product_brands.append(brand_dict)
    return jsonify(product_brands), 200


@app_views.route(
    "products/<product_id>/brands/<brand_id>",
    strict_slashes=False,
    methods=["GET"]
)
@admin_only
def get_product_brand(product_id: str, brand_id: str):
    """
    Get a single brand linked to a product.
    """
    product = get_obj(Product, product_id)
    if not product:
        abort(404, description="Product does not exist")

    brand = get_obj(Brand, brand_id)
    if not brand:
        abort(404, description="Brand does not exist")

    brand_dict = get_brand_dict(brand)
    return jsonify(brand_dict), 200


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
