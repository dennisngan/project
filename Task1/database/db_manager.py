from __future__ import annotations

import sqlite3
from config import DB_PATH


class DatabaseManager:
    """
    Singleton wrapper around a SQLite connection.
    Use DatabaseManager.get_instance() — never call __init__ directly.
    """
    _instance: DatabaseManager | None = None

    def __init__(self, db_path: str = DB_PATH):
        if DatabaseManager._instance is not None:
            raise RuntimeError(
                "Use DatabaseManager.get_instance() instead of constructing directly."
            )
        self._db_path = db_path
        self._connection: sqlite3.Connection = self._connect()
        self._create_tables()

    @classmethod
    def get_instance(cls, db_path: str = DB_PATH) -> DatabaseManager:
        """Return the singleton instance, creating it on first call."""
        if cls._instance is None:
            obj = object.__new__(cls)
            obj._db_path = db_path
            obj._connection = obj._connect()
            obj._create_tables()
            cls._instance = obj
        return cls._instance

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # rows as dict-like objects
        conn.execute("PRAGMA foreign_keys = ON")  # enforce foreign key constraints
        conn.execute("PRAGMA journal_mode = WAL")  # concurrent read/write
        return conn

    def _create_tables(self):
        """Create all tables if they don't already exist."""
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories
            (
                category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS products
            (
                product_id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT    NOT NULL,
                price          REAL    NOT NULL CHECK (price >= 0),
                cost_price     REAL    NOT NULL CHECK (cost_price >= 0),
                stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
                category_id    INTEGER REFERENCES categories (id) ON DELETE SET NULL,
                is_active      INTEGER NOT NULL DEFAULT 1
                );

            CREATE TABLE IF NOT EXISTS users
            (
                user_id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name     TEXT NOT NULL,
                role          TEXT NOT NULL CHECK (role IN ('cashier', 'manager'))
                );           
            """
        )

        self._connection.commit()

    # Helper methods
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single statement and return the cursor."""
        return self._connection.execute(sql, params)

    def executemany(self, sql: str, params_list) -> sqlite3.Cursor:
        return self._connection.executemany(sql, params_list)

    def commit(self):
        self._connection.commit()

    def fetchall(self, sql: str, params: str = ()) -> list[sqlite3.Row]:
        return self._connection.execute(sql, params).fetchall()

    def fetchone(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        return self._connection.execute(sql, params).fetchone()

    def get_last_insert_id(self) -> int:
        """Get the ID of the last inserted row. Must be called immediately after an insert."""
        row = self._connection.execute("SELECT last_insert_rowid()").fetchone()
        return row[0]

    def close(self):
        """Close the database connection and reset the singleton instance."""
        self._connection.close()
        DatabaseManager._instance = None


"""Test the DatabaseManager singleton behavior."""
if __name__ == "__main__":
    import tempfile, pathlib
    tmp = pathlib.Path(tempfile.mktemp(suffix=".db"))
    db1 = DatabaseManager.get_instance(str(tmp))
    tables = db1.fetchall("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables created:", [t["name"] for t in tables])
    db2 = DatabaseManager.get_instance(str(tmp))
    assert db1 is db2, "Singleton broken — two different instances!"
    db1.close()
    tmp.unlink(missing_ok=True)
    print("DatabaseManager singleton test passed.")