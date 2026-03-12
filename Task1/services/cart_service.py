import copy

from models.cart_item import CartItem


class Cart:
    def __init__(self):
        """private list — never accessed directly from outside"""
        self.__items: list[CartItem] = []

    def add_item(self, product_id: int, name: str, unit_price: float
                 , category_id: int, quantity: int = 1) -> None:
        """Add *quantity* units of a product. If already in cart, increment qty."""
        for item in self.__items:
            if item.product_id == product_id:
                item.quantity += quantity
                return

        self.__items.append(CartItem(product_id, name, unit_price, quantity, category_id))

    def remove_item(self, product_id: int) -> bool:
        """Remove a product entirely. Returns True if it was found."""
        for i, item in enumerate(self.__items):
            if item.product_id == product_id:
                self.__items.pop(i)
                return True
        return False

    def update_quantity(self, product_id: int, quantity: int) -> bool:
        """Set qty for a product. Removes item if qty ≤ 0."""
        for item in self.__items:
            if item.product_id == product_id:
                new_qty = item.quantity + quantity
                if new_qty <= 0:
                    return self.remove_item(product_id)
                item.quantity = new_qty
                return True
        return False

    def clear(self) -> None:
        """Empty the cart."""
        self.__items.clear()

    def get_items(self) -> list[CartItem]:
        """Return a deep copy of all items to prevent external mutation."""
        return copy.deepcopy(self.__items)

    def get_item(self, product_id: int) -> CartItem | None:
        for item in self.__items:
            if item.product_id == product_id:
                return item
        return None

    def is_empty(self) -> bool:
        return len(self.__items) == 0

    # --- Totals ---

    def get_total(self) -> float:
        return round(sum(item.line_total for item in self.__items), 2)

    def __str__(self) -> str:
        if self.is_empty():
            return "Cart is empty."
        lines = [str(item) for item in self.__items]
        lines.append(f"{'─' * 40}")
        lines.append(f"TOTAL: ${self.get_total():.2f}")
        return "\n".join(lines)
