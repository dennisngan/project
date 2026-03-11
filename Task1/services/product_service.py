from database.db_manager import DatabaseManager
from models.product import Product


class ProductService:
    def __init__(self, db: DatabaseManager):
        self._db = db

    def get_all_products(self) -> list[Product]:
        sql = "SELECT * FROM products WHERE is_active = 1"
        rows = self._db.fetchall(sql)
        return [Product.from_db_row(row) for row in rows]

    def get_product_by_id(self, product_id) -> Product | None:
        sql = "SELECT * FROM products WHERE product_id = ?"
        row = self._db.fetchone(sql, (product_id,))
        return Product.from_db_row(row) if row else None

    def create_product(self, name: str, price: float, cost_price: float, stock_quantity: int, category_id: int,
                       is_active: bool) -> Product | None:
        sql = """INSERT INTO products (name, price, cost_price, stock_quantity, category_id, is_active)
                 VALUES (?, ?, ?, ?, ?, ?)"""
        self._db.execute(sql, (name, price, cost_price, stock_quantity, category_id, int(is_active)))
        self._db.commit()
        new_id = self._db.get_last_insert_id()
        return self.get_product_by_id(new_id)

    def update_product(self, product_id: int, name: str, price: float, cost_price: float, stock_quantity: int,
                       category_id: int,
                       is_active: bool):
        sql = """UPDATE products
                 SET name=?,
                     price=?,
                     cost_price=?,
                     stock_quantity=?,
                     category_id=?,
                     is_active=?
                 WHERE product_id = ?
              """
        self._db.execute(sql, (name, price, cost_price, stock_quantity, category_id, int(is_active), product_id))
        self._db.commit()
        return self.get_product_by_id(product_id)

    def update_stock(self, product_id: int, quantity_to_deduct: int, commit: bool = False) -> Product:
        """Deduct stock for a product. Raises ValueError if insufficient stock."""
        product = self.get_product_by_id(product_id)
        if product is None:
            raise ValueError(f"Product {product_id} not found.")
        if product.stock_quantity < quantity_to_deduct:
            raise ValueError(
                f"Insufficient stock for product '{product.name}': "
                f"available={product.stock_quantity}, requested={quantity_to_deduct}"
            )

        sql = "UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?"
        self._db.execute(sql, (quantity_to_deduct, product_id))
        if commit:
            self._db.commit()
        return self.get_product_by_id(product_id)

    def delete_product(self, product_id) -> bool:
        sql = "DELETE FROM products WHERE product_id = ?"
        cursor = self._db.execute(sql, (product_id,))
        self._db.commit()

        return cursor.rowcount > 0
