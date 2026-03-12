DB_PATH = "smartpos.db"

# Store identity (used on printed receipts)
STORE_NAME = "Quick Store"
STORE_ADDRESS = "G/F HKMU, Hong Kong"
STORE_PHONE = "Tel: +852 1234 5678"

# The number of rounds to use for bcrypt hashing
SALT_ROUNDS = 12

# When stock quantity falls below this level, show a warning in the UI
LOW_STOCK_THRESHOLD = 5

# Category colors for product cards (category name → hex color code)
CATEGORY_COLORS = {
    "drinks":        "#3A82F7",   # Blue
    "snacks":        "#F97316",   # Orange
    "dairy":         "#06B6D4",   # Cyan
    "bakery":        "#D97706",   # Amber
    "frozen":        "#8B5CF6",   # Violet
    "household":     "#10B981",   # Emerald
    "personal care": "#EC4899",   # Pink
    "other":         "#9CA3AF",   # Cool gray
}