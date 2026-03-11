import sqlite3
from abc import ABC, abstractmethod
from typing import Self


class BaseModel(ABC):
    """Abstract base class for all models. Enforces that subclasses implement from_db_row()."""

    @classmethod
    @abstractmethod
    def from_db_row(cls, row: sqlite3.Row) -> Self:
        """
        Enforce that subclasses implement a from_db_row() factory method.
        This method should take a database row (e.g. sqlite3.Row) and return an instance of the model.
        """
        pass

