from config import CATEGORY_COLORS
from models.product import Product
from services.category_cache import CategoryCache


def get_category_color(product: Product) -> str:
    category_map = CategoryCache.get_map()
    category_name = category_map.get(product.category_id)
    return CATEGORY_COLORS.get(category_name.name.lower())
