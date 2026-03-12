from constant.enums import UserRole
from database.db_manager import DatabaseManager
from exceptions import WeakPasswordException, UsernameTakenException
from models.user import User
from utils import password_utils


class UserService:
    def __init__(self, db: DatabaseManager):
        self._db = db

    def get_all_user(self) -> list[User]:
        """Return all users ordered by role then name."""
        sql = "SELECT * FROM users ORDER BY role, full_name"
        rows = self._db.fetchall(sql)
        return [User.from_db_row(row) for row in rows]

    def exist_username(self, username: str) -> bool:
        """Return True if the given username already exists."""
        sql = "SELECT 1 FROM users WHERE username = ?"
        row = self._db.fetchone(sql, (username,))
        return row is not None

    def create_user(self, username: str, full_name: str, password: str, role: UserRole) -> User | None:
        """Create a new user account. Returns the created User object or None on failure."""
        if len(password) < 6:
            raise WeakPasswordException("Password must be at least 6 characters.")

        if self.exist_username(username):
            raise UsernameTakenException("That username already exists.")

        hashed_password = password_utils.hash_password(password)
        sql = "INSERT INTO users (username, password_hash, full_name, role) VALUES (?,?,?,?)"
        self._db.execute(sql, (username, hashed_password, full_name, role.value))

        user_id = self._db.get_last_insert_id()
        self._db.commit()
        return User(user_id, username, full_name=full_name, role=role)

    def get_user_by_username(self, username: str) -> User | None:
        """Return a User object for the given username, or None if not found."""
        sql = "SELECT * FROM users WHERE username = ?"
        row = self._db.fetchone(sql, (username,))
        if row:
            return User.from_db_row(row)
        return None
