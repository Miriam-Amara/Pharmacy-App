#!/usr/bin/env python3

"""
"""

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, select, func
from typing import Any, Sequence, Type, TypeVar

from basemodel import Base, BaseModel
from brand import Brand, brand_products
from category import Category
from employee import Employee
from product import Product
from purchase_order import PurchaseOrder
from purchase_order_items import PurchaseOrderItem
from sale import Sale
from stock_level import StockLevel


T = TypeVar("T", bound=BaseModel)

class DBStorage:
    """
    """
    __classes: list[Type[BaseModel]] = [
        Brand, Category, Employee, Product,
        PurchaseOrder, PurchaseOrderItem, Sale, StockLevel,
    ]
    def __init__(self, database_url: str) -> None:
        """
        """
        self.__engine = create_engine(database_url, pool_pre_ping=True)
    
    def all(self, cls: Type[T], page_size: int, page_num: int) -> Sequence[T]:
        """
        """
        if cls not in self.__classes:
            raise TypeError("Invalid class")
        if not isinstance(page_size, int): # type: ignore
            raise TypeError("Page size must be a valid integer")
        if not isinstance(page_num, int): # type: ignore
            raise TypeError("Page number must be a valid integer")
        if page_size <= 0:
            raise ValueError("Page size must be greater than 0")
        if page_num <= 0:
            raise ValueError("Page number must be greater than 0")
        
        cls_objects = self.__session.scalars(
            select(cls)
            .offset((page_num - 1) * page_size)
            .limit(page_size)
        ).all()

        return cls_objects

    def count(self, cls: Type[T] | None = None) -> int | dict[str, Any] | None:
        """
        """
        if cls in self.__classes:
            count_cls_objects: int | None = self.__session.scalar(
                select(func.count()).select_from(cls)
            )
            return count_cls_objects
        
        count_all_objects: dict[str, Any] = {}
        for cls_name in self.__classes:
            count_cls_obj = self.__session.scalar(
                select(func.count()).select_from(cls_name)
            )
            count_all_objects[cls_name.__name__] = count_cls_obj
        return count_all_objects

    def close(self):
        """
        """
        self.__session.close()

    def get_obj_by_id(self, cls: Type[T], id: str) -> Type[T] | None:
        """
        """
        if cls in self.__classes:
            obj = self.__session.get(cls, id)
            return obj

    def new(self, obj: BaseModel):
        """
        """
        self.__session.add(obj)

    def reload(self):
        """
        """
        Base.metadata.create_all(self.__engine)
        self.__session = scoped_session(
            sessionmaker(bind=self.__engine, expire_on_commit=False)
        )

    def save(self):
        """
        """
        try:
            self.__session.commit()
        except Exception:
            self.__session.rollback()
            raise
