from database.db_manager import DatabaseManager
from models.category import Category


class CategoryCache:
    """Caches category_id → Category mappings to avoid repeated DB queries."""
    _cache: dict[int, Category] | None = None

    @classmethod
    def get_map(cls) -> dict[int, Category]:
        if cls._cache is None:
            db = DatabaseManager.get_instance()
            sql = "SELECT * FROM categories"
            rows = db.fetchall(sql)
            cls._cache = {row["category_id"]: Category.from_db_row(row) for row in rows}
        return cls._cache

    @classmethod
    def invalidate(cls):
        cls._cache = None

    @classmethod
    def get_name(cls, category_id: int) -> str | None:
        category = cls.get_map().get(category_id)
        return category.name if category else None
