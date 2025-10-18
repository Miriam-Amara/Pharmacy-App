#!/usr/bin/env python3

"""
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Float

from basemodel import Base, BaseModel
from brand import brand_products


class Product(BaseModel, Base):
    """
    """
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
        back_populates="products"
    )
    sales = relationship("Sale", back_populates="product")
    purchases = relationship("PurchaseOrderItem", back_populates="product")
    stock_levels = relationship("StockLevel", back_populates="product")
    added_by = relationship("Employee", backref="products_added")
