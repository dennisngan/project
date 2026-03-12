from config import CATEGORY_COLORS
from gui.styles import Colors
from models.product import Product
from services.category_cache import CategoryCache


def get_category_color(product: Product) -> str:
    category_map = CategoryCache.get_map()
    category = category_map.get(product.category_id)
    if category is None:
        return Colors.BORDER
    return CATEGORY_COLORS.get(category.name.lower(), Colors.BORDER)
