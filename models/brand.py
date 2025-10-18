#!/usr/bin/env python3

"""
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Table, Column, ForeignKey, String, Boolean

from basemodel import Base, BaseModel


brand_products = Table(
    "brand_products",
    Base.metadata,
    Column(
        "brand_id",
        String(36),
        ForeignKey("brands.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "product_id",
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    )
)


class Brand(BaseModel, Base):
    """
    """
    __tablename__ = "brands"

    name = mapped_column(String(200), nullable=False)
    is_active = mapped_column(Boolean, default=True)
    employee_id = mapped_column(
        String(36),
        ForeignKey("employees.id"),
        nullable=False,
        ondelete="SET NULL"
    )
    added_by = relationship("Employee", backref="brands")
    products = relationship(
        "Product", secondary=brand_products, back_populates="brands"
    )
    sales = relationship("Sale", back_populates="brand")
    purchase_orders = relationship("PurchaseOrder", back_populates="brand")
