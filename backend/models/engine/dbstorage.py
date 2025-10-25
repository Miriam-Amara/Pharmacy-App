#!/usr/bin/env python3

"""
Database storage engine for managing all model interactions.
"""

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, select, func, Select
from typing import Any, Sequence, Type, TypeVar, Tuple
import logging

from models.basemodel import Base, BaseModel
from models.brand import Brand, brand_products
from models.category import Category
from models.employee import Employee
from models.employee_session import EmployeeSession
from models.product import Product
from models.purchase_order import PurchaseOrder
from models.purchase_order_item import PurchaseOrderItem
from models.sale import Sale
from models.stock_level import StockLevel


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class DBStorage:
    """Handles all database operations for the application."""

    __classes: list[Type[BaseModel]] = [
        Brand,
        Category,
        Employee,
        Product,
        PurchaseOrder,
        PurchaseOrderItem,
        Sale,
        StockLevel,
        EmployeeSession,
    ]

    def __init__(self, database_url: str) -> None:
        """Initializes the database engine with the provided URL."""
        self.__engine = create_engine(database_url, pool_pre_ping=True)

    def all(self, cls: Type[T], page_size: int, page_num: int) -> Sequence[T]:
        """
        Returns paginated results for all records of a given model class.
        """
        if not issubclass(cls, BaseModel):  # type: ignore
            raise TypeError("Cls must inherit from BaseModel")
        if not isinstance(page_size, int):  # type: ignore
            raise TypeError("Page size must be a valid integer")
        if not isinstance(page_num, int):  # type: ignore
            raise TypeError("Page number must be a valid integer")
        if page_size <= 0:
            raise ValueError("Page size must be greater than 0")
        if page_num <= 0:
            raise ValueError("Page number must be greater than 0")

        cls_objects = self.__session.scalars(
            select(cls).offset((page_num - 1) * page_size).limit(page_size)
        ).all()

        return cls_objects

    def count(self, cls: Type[T] | None = None) -> int | dict[str, Any] | None:
        """Returns the count of records for a model or all models."""
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
        """Closes the current database session."""
        self.__session.close()

    def delete(self, obj: BaseModel) -> None:
        """Deletes an object from the current session."""
        self.__session.delete(obj)

    def get_obj_by_id(self, cls: Type[T], id: str) -> T | None:
        """Fetches a single object by its ID."""
        if issubclass(cls, BaseModel):  # type: ignore
            obj = self.__session.get(cls, id)
            return obj

    def new(self, obj: BaseModel):
        """Adds a new object to the current session."""
        self.__session.add(obj)

    def reload(self):
        """Creates all tables and initializes a scoped session."""
        Base.metadata.create_all(self.__engine)
        self.__session = scoped_session(
            sessionmaker(bind=self.__engine, expire_on_commit=False)
        )

    def save(self):
        """Commits all pending changes to the database."""
        try:
            self.__session.commit()
        except Exception as e:
            try:
                self.__session.rollback()
            except Exception as rollback_error:
                logger.critical(f"Rollback failed: {rollback_error}")
            raise e

    def search_employee_by_email_username(
        self, email: str | None = None, username: str | None = None
    ) -> Employee | None:
        """Finds an employee by email or username."""
        if not email and not username:
            raise ValueError("Either email or username is required")

        stmt: Select[Tuple[Employee]] | None = None
        if email:
            stmt = select(Employee).where(Employee.email == email)
        else:
            stmt = select(Employee).where(Employee.username == username)
        employee = self.__session.scalars(stmt).one_or_none()
        return employee
