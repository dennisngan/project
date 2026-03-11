DB_PATH = "smartpos.db"

# The number of rounds to use for bcrypt hashing
SALT_ROUNDS = 12

# When stock quantity falls below this level, show a warning in the UI
LOW_STOCK_THRESHOLD = 5


CATEGORY_COLORS = {
    "drinks":        "#3A82F7",   # Blue
    "snacks":        "#F97316",   # Orange
    "dairy":         "#06B6D4",   # Cyan
    "bakery":        "#D97706",   # Amber
    "frozen":        "#8B5CF6",   # Violet
    "household":     "#10B981",   # Emerald
    "personal Care": "#EC4899",   # Pink
    "other":         "#9CA3AF",   # Cool gray
}