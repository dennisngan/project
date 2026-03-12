from dataclasses import dataclass


@dataclass
class CartItem:
    """A single line in the cart: product snapshot + quantity."""
    product_id: int
    name: str
    unit_price: float
    quantity: int
    category_id: int

    @property
    def line_total(self) -> float:
        return round(self.unit_price * self.quantity, 2)

    def __str__(self) -> str:
        return f"{self.name} x{self.quantity} @ ${self.unit_price:.1f} = ${self.line_total:.1f}"
