from __future__ import annotations

from models.base import BaseModel


class Product(BaseModel):

    def __init__(
            self,
            product_id: int,
            name: str,
            price: float,
            cost_price: float,
            stock_quantity: int,
            category_id: int,
            is_active: bool = True,
    ):
        self.product_id = product_id
        self.name = name
        self.price = float(price)
        self.cost_price = float(cost_price)
        self.stock_quantity = int(stock_quantity)
        self.category_id = category_id
        self.is_active = is_active

    def __str__(self) -> str:
        return f"{self.name} — {Product.format_price(self.price)} (stock: {self.stock_quantity})"

    def __repr__(self) -> str:
        return f"<Product id={self.product_id} name={self.name!r}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.product_id == other.product_id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.name.lower() < other.name.lower()

    @staticmethod
    def format_price(amount: float) -> str:
        """Format a float as a currency string, e.g. 3.0 → '$3.0'."""
        return f"${amount:,.1f}"

    @classmethod
    def from_db_row(cls, row) -> Product:
        return Product(
            product_id=row["id"],
            name=row["name"],
            price=row["price"],
            cost_price=row["cost_price"],
            stock_quantity=row["stock_quantity"],
            category_id=row["category_id"] or 0,
            is_active=bool(row["is_active"]),
        )

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "cost_price": self.cost_price,
            "stock_quantity": self.stock_quantity,
            "category_id": self.category_id,
            "is_active": self.is_active,
        }
