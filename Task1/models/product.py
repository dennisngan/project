from __future__ import annotations

import sqlite3

from models.base import BaseModel


class Product(BaseModel):
    """
    Domain model for a store product.
    """

    def __init__(
            self,
            product_id: int,
            name: str,
            price: float,
            cost_price: float,
            stock_quantity: int,
            category_id: int,
    ):
        self.product_id = product_id
        self.name = name
        self.price = float(price)
        self.cost_price = float(cost_price)
        self.stock_quantity = int(stock_quantity)
        self.category_id = category_id

    def __str__(self) -> str:
        return f"{self.name} — {Product.format_price(self.price)} (stock: {self.stock_quantity})"

    def __repr__(self) -> str:
        return f"<Product id={self.product_id} name={self.name!r}>"

    def __eq__(self, other) -> bool:
        # Identity is based on product_id, not object reference
        if not isinstance(other, Product):
            return NotImplemented
        return self.product_id == other.product_id

    def __hash__(self) -> int:
        # Must be defined alongside __eq__ so Products can be used as dict keys / in sets.
        return hash(self.product_id)

    def __lt__(self, other) -> bool:
        # Enables alphabetical sorting (e.g. sorted(products)) without a separate key function.
        if not isinstance(other, Product):
            return NotImplemented
        return self.name.lower() < other.name.lower()

    @staticmethod
    def format_price(amount: float) -> str:
        """Format a float as a currency string, e.g. 3.0 → '$3.0'."""
        return f"HKD${amount:,.1f}"

    @classmethod
    def from_db_row(cls, row: sqlite3.Row) -> Product:
        return cls(
            product_id=row["product_id"],
            name=row["name"],
            price=row["price"],
            cost_price=row["cost_price"],
            stock_quantity=row["stock_quantity"],
            category_id=row["category_id"] or 0,
        )

