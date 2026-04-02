from constant.enums import UserRole
from database.db_manager import DatabaseManager
from services.product_service import ProductService
from services.user_service import UserService


def seed_categories(db: DatabaseManager):
    """Insert default categories"""

    count = db.fetchone("SELECT COUNT(*) AS count FROM categories")["count"]
    if count > 0:
        return

    categories = [
        (1, "Drinks"),
        (2, "Snacks"),
        (3, "Dairy"),
        (4, "Bakery"),
        (5, "Frozen"),
        (6, "Household"),
        (7, "Personal Care"),
        (8, "Other"),
    ]

    sql = "INSERT INTO categories (category_id, name) VALUES (?,?)"

    db.executemany(sql, [(category_id, name) for category_id, name in categories])


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


def seed_products(db: DatabaseManager):
    """Insert default products with categories."""
    count = db.fetchone("SELECT COUNT(*) as count FROM products")["count"]
    if count > 0:
        return

    products = [
        # (name,                    price,   cost,  stock, cat_id)

        # 1 - Drinks
        ('Coca-Cola 355ml'         ,  8.5,   4.0,  200,  1),
        ('Pepsi 355ml'             ,  8.5,   4.0,  150,  1),
        ('Water 500ml'             ,  6.0,   2.5,  300,  1),
        ('Red Bull 250ml'          , 17.0,   9.0,   80,  1),
        ('Orange Juice 1L'         , 22.0,  12.0,   60,  1),

        # 2 - Snacks
        ("Lay's Classic 200g"      , 22.0,  11.0,  120,  2),
        ('Doritos Nacho 200g'      , 22.0,  11.0,  110,  2),
        ('Kit Kat 45g'             , 11.0,   5.5,  150,  2),
        ('Snickers 52g'            , 11.0,   5.5,  140,  2),

        # 3 - Dairy
        ('Milk 2L'                 , 32.0,  20.0,   50,  3),
        ('Cheddar Cheese 400g'     , 52.0,  32.0,   40,  3),
        ('Greek Yogurt 500g'       , 38.0,  22.0,   45,  3),

        # 4 - Bakery
        ('White Bread'             , 20.0,   9.0,   70,  4),
        ('Bagels 6pk'              , 32.0,  15.0,   35,  4),

        # 5 - Frozen
        ('Frozen Pizza'            , 62.0,  35.0,   30,  5),
        ('Ice Cream 1L'            , 45.0,  25.0,   25,  5),

        # 6 - Household
        ('Paper Towels 2pk'        , 28.0,  13.0,   90,  6),
        ('Dish Soap 500ml'         , 25.0,  11.0,   75,  6),

        # 7 - Personal Care
        ('Shampoo 400ml'           , 52.0,  25.0,   55,  7),
        ('Toothpaste 120g'         , 28.0,  13.0,   60,  7),

        # 8 - Other
        ('Tylenol 24ct'            , 72.0,  38.0,   40,  8),
        ('Deli Ham 200g'           , 55.0,  35.0,   20,  8),
    ]

    product_service = ProductService(db)
    for name, price, cost, stock, cat_id in products:
        product_service.create_product(name, price, cost, stock, cat_id)

    print(f"Seeded {len(products)} products.")


def run_seed():
    """Main entry: seed all data."""
    try:
        db = DatabaseManager.get_instance()
        seed_categories(db)
        seed_users(db)
        seed_products(db)
        print("Database seeding complete.")
    except Exception as e:
        print(f"Seeding failed: {e}")
        raise
