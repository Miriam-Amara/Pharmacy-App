#!/usr/bin/env python3

"""
Product model.
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Float

from models.basemodel import Base, BaseModel
from models.brand import brand_products


class Product(BaseModel, Base):
    """Represents a product in the pharmacy."""

    __tablename__ = "products"

    name = mapped_column(String(500), nullable=False)
    selling_price = mapped_column(Float, default=0.00)
    category_id = mapped_column(
        String(36),
        ForeignKey("categories.id", ondelete="SET NULL"),
    )
    employee_id = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="SET NULL"),
    )
    category = relationship("Category", back_populates="products")
    brands = relationship(
        "Brand",
        secondary=brand_products,
        back_populates="products",
        passive_deletes=True,
    )
    sales = relationship("Sale", back_populates="product")
    purchases = relationship("PurchaseOrderItem", back_populates="product")
    stock_levels = relationship("StockLevel", back_populates="product")
    added_by = relationship("Employee", backref="products_added")
