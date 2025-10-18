#!/usr/bin/env python3

"""
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Float

from basemodel import Base, BaseModel


class Sale(BaseModel, Base):
    """
    """
    __tablename__ = "sales"

    product_id = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="SET NULL")
    )
    brand_id = mapped_column(
        String(36),
        ForeignKey("brands.id", ondelete="SET NULL")
    )
    quantity = mapped_column(Integer, nullable=False)
    unit_selling_price = mapped_column(Float, nullable=False)
    total_selling_price = mapped_column(Float, nullable=False)
    employee_id = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="SET NULL")
    )
    product = relationship("Product", back_populates="sales")
    brand = relationship("Sale", back_populates="sales")
    added_by = relationship("Employee", backref="sales")
