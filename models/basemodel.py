#!/usr/bin/env pythonn3


"""

"""

from copy import deepcopy
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import String, DateTime
from typing import Any
from uuid import uuid4


class Base(DeclarativeBase):
    pass


class BaseModel:
    """
    """
    id = mapped_column(String(36), primary_key=True, sort_order=-1)
    created_at = mapped_column(DateTime, default=datetime.now, sort_order=-2)
    last_updated = mapped_column(DateTime, default=datetime.now, sort_order=-3)

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        """
        """
        self.id = str(uuid4())
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        if kwargs:
            kwargs.pop("id", None)
            kwargs.pop("created_at", None)
            kwargs.pop("last_updated", None)
            self.__dict__.update(kwargs)
    
    def __str__(self) -> str:
        """
        """
        obj_dict = deepcopy(self.__dict__)
        obj_dict.pop("_sa_instance", None)
        obj_dict["created_at"] = self.created_at.isoformat()
        obj_dict["last_updated"] = self.last_updated.isoformat()
        return f"[{self.__class__.__name__}.{self.id}] ({obj_dict})"

    def delete(self) -> None:
        pass

    def get_enum_value(self, obj_dict: dict[str, Any]) -> dict[str, Any]:
        """
        """
        for attr, val in obj_dict.items():
            if isinstance(val, Enum):
                obj_dict[attr] = val.value
        return obj_dict

    def save(self) -> None:
        """
        """
        self.last_updated = datetime.now()
        

    def to_dict(self) -> dict[str, Any]:
        """
        """
        obj_dict = deepcopy(self.__dict__)
        obj_dict.pop("_sa_instance_state", None)
        obj_dict["__class__"] = self.__class__.__name__
        obj_dict = self.get_enum_value(obj_dict)
        return obj_dict
