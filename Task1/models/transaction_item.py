from __future__ import annotations

import sqlite3

from models.base import BaseModel


class TransactionItem(BaseModel):
    """
    Represents a single line item in a completed transaction.
    """
    def __init__(
            self,
            transaction_item_id: int,
            transaction_id: int,
            product_id: int | None,  # nullable — product may be deleted
            product_name: str,
            quantity: int,
            unit_price: float,
            line_total: float,
    ):
        self.transaction_item_id = transaction_item_id
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = float(unit_price)
        self.line_total = float(line_total)

    @classmethod
    def from_db_row(cls, row: sqlite3.Row) -> TransactionItem:
        return cls(
            transaction_item_id=row["transaction_item_id"],
            transaction_id=row["transaction_id"],
            product_id=row["product_id"],
            product_name=row["product_name"],
            quantity=row["quantity"],
            unit_price=row["unit_price"],
            line_total=row["line_total"],
        )

    def __str__(self) -> str:
        return f"{self.product_name} x{self.quantity} @ ${self.unit_price:.1f} = ${self.line_total:.1f}"

    def __repr__(self) -> str:
        return f"<TransactionItem id={self.transaction_item_id} product_id={self.product_id}>"
