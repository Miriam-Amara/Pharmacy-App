#!/usr/bin/env python3

"""
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer

from basemodel import Base, BaseModel


class StockLevel(BaseModel, Base):
    """
    """
    __tablename__ = "stock_levels"

    product_id = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="SET NULL")
    )
    brand_id = mapped_column(
        String(36),
        ForeignKey("brands.id", ondelete="SET NULL")
    )
    current_stock = mapped_column(Integer, default=0)
    product = relationship("Product", back_populates="stock_levels")
    brand = relationship("Brand", back_populates="stock_levels")
