class Validators:
    """Collection of static validation methods."""

    @staticmethod
    def is_valid_price(value) -> bool:
        """Price must be a non-negative number."""
        try:
            return float(value) >= 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def is_valid_stock(value) -> bool:
        """Stock must be a non-negative integer number."""
        try:
            return int(value) >= 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def is_valid_product_name(name: str) -> bool:
        """Product name: 1–100 non-empty characters."""
        return isinstance(name, str) and 1 <= len(name.strip()) <= 100
