from database.db_manager import DatabaseManager
from models.product import Product


class ProductService:
    """
    Service layer for all product-related database operations (CRUD).

    Receives a DatabaseManager via Dependency Injection (constructor parameter)
    rather than calling DatabaseManager.get_instance() directly — this keeps the
    service testable and decoupled from the singleton.
    All database references are stored as private attributes (_db) to enforce Encapsulation.
    """
    def __init__(self, db: DatabaseManager):
        self._db = db

    def get_all_products(self) -> list[Product]:
        sql = "SELECT * FROM products"
        rows = self._db.fetchall(sql)
        return [Product.from_db_row(row) for row in rows]

    def get_product_by_id(self, product_id) -> Product | None:
        sql = "SELECT * FROM products WHERE product_id = ?"
        row = self._db.fetchone(sql, (product_id,))
        return Product.from_db_row(row) if row else None

    def create_product(self, name: str, price: float, cost_price: float, stock_quantity: int,
                       category_id: int) -> Product | None:
        sql = """INSERT INTO products (name, price, cost_price, stock_quantity, category_id)
                 VALUES (?, ?, ?, ?, ?)"""
        self._db.execute(sql, (name, price, cost_price, stock_quantity, category_id))
        self._db.commit()
        new_id = self._db.get_last_insert_id()
        return self.get_product_by_id(new_id)

    def update_product(self, product_id: int, name: str, price: float, cost_price: float, stock_quantity: int,
                       category_id: int):
        sql = """UPDATE products
                 SET name=?,
                     price=?,
                     cost_price=?,
                     stock_quantity=?,
                     category_id=?
                 WHERE product_id = ?
              """
        self._db.execute(sql, (name, price, cost_price, stock_quantity, category_id, product_id))
        self._db.commit()
        return self.get_product_by_id(product_id)

    def update_stock(self, product_id: int, quantity_to_deduct: int, commit: bool = False) -> Product:
        """Deduct stock for a product atomically. Raises ValueError if insufficient stock."""
        sql = (
            "UPDATE products SET stock_quantity = stock_quantity - ? "
            "WHERE product_id = ? AND stock_quantity >= ?"
        )
        cursor = self._db.execute(sql, (quantity_to_deduct, product_id, quantity_to_deduct))
        if cursor.rowcount == 0:
            product = self.get_product_by_id(product_id)
            if product is None:
                raise ValueError(f"Product {product_id} not found.")
            raise ValueError(
                f"Insufficient stock for product '{product.name}': "
                f"available={product.stock_quantity}, requested={quantity_to_deduct}"
            )
        if commit:
            self._db.commit()
        return self.get_product_by_id(product_id)

    def delete_product(self, product_id) -> bool:
        sql = "DELETE FROM products WHERE product_id = ?"
        cursor = self._db.execute(sql, (product_id,))
        self._db.commit()

        return cursor.rowcount > 0

    def search_product(self, query: str) -> list[Product]:
        """Search products by name or ID. Case-insensitive substring match for name, exact match for ID."""
        if not query:
            return self.get_all_products()

        q = query.lower()
        match = []
        for p in self.get_all_products():
            if q in str(p.product_id) or q in p.name.lower():
                match.append(p)
        return match
