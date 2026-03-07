from constant.enums import UserRole
from database.db_manager import DatabaseManager
from services.user_service import UserService


def seed_categories(db: DatabaseManager):
    """Insert default categories"""

    count = db.fetchone("SELECT COUNT(*) AS count FROM categories")["count"]
    if count > 0:
        return

    categories = [
        "Drinks",
        "Snacks",
        "Dairy",
        "Bakery",
        "Frozen",
        "Household"
    ]

    sql = "INSERT INTO categories (name) VALUES (?)"

    db.executemany(sql, [(name,) for name in categories])


def seed_users(db: DatabaseManager):
    """Insert default manager and cashier accounts if none exist."""
    count = db.fetchone("SELECT COUNT(*) as count FROM users")["count"]
    if count > 0:
        return

    users = [
        ("admin", "admin123", "Max Leung", "manager"),
        ("cashier1", "cash123", "Peter Kwan", "cashier"),
        ("cashier2", "cash123", "May Chan", "cashier"),
    ]
    user_service = UserService(db)
    for username, password, full_name, role in users:
        user_service.create_user(username, full_name, password, UserRole(role))

    print(f"Seeded {len(users)} users.")


def run_seed():
    """Main entry: seed all data."""
    try:
        db = DatabaseManager.get_instance()
        seed_categories(db)
        seed_users(db)
        print("Database seeding complete.")
    except Exception as e:
        print(f"Seeding failed: {e}")
        raise
