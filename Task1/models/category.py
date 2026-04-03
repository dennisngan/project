from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from models.base import BaseModel


@dataclass
class Category(BaseModel):
    """
    Product category model.

    Uses Python's @dataclass decorator to auto-generate __init__, __repr__, and __eq__,
    while still inheriting the abstract from_db_row() contract from BaseModel (ABC).
    The all() class method acts as a factory that returns a sentinel 'All' category
    (id=0) used by the UI to represent the unfiltered view.
    """

    category_id: int
    name: str

    def __str__(self) -> str:
        return f"Category(category_id={self.category_id}, name='{self.name}')"

    @classmethod
    def from_db_row(cls, row: sqlite3.Row) -> Category:
        return cls(
            category_id=row["category_id"],
            name=row["name"]
        )

    @classmethod
    def all(cls):
        return Category(
            category_id=0,
            name="All"
        )
