from __future__ import annotations

import sqlite3

from constant.enums import UserRole
from constant.permission import has_permission, Permission
from models.base import BaseModel


class User(BaseModel):
    """
    Password hashing is handled separately in the UserService
    The password hash is only needed at login for security reasons, so it's not stored in the User object after authentication.
    """

    def __init__(
            self,
            user_id: int,
            username: str,
            full_name: str,
            role: UserRole,
    ):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self._role = role

    def __str__(self) -> str:
        return f"{self.full_name} (@{self.username}) [{self._role.name}]"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.user_id} username={self.username!r}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        return hash(self.user_id)

    @classmethod
    def from_db_row(cls, row: sqlite3.Row) -> User:
        """
        Polymorphic factory method: returns a Manager or Cashier subclass instance
        depending on the 'role' value stored in the database row.
        Callers receive a User reference but get role-specific behavior at runtime.
        """
        role = row["role"]

        if role == UserRole.MANAGER:
            return Manager(
                user_id=row["user_id"],
                username=row["username"],
                full_name=row["full_name"],
            )

        return Cashier(
            user_id=row["user_id"],
            username=row["username"],
            full_name=row["full_name"],
        )

    def can_manage_products(self) -> bool:
        return has_permission(self._role, Permission.MANAGE_PRODUCTS)

    def can_manage_user(self) -> bool:
        return has_permission(self._role, Permission.MANAGE_USERS)

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def display_name(self) -> str:
        """Display first name for compact UI display"""
        return self.full_name.split()[0] if self.full_name else self.username

class Manager(User):
    """
    Concrete subclass of User for manager accounts.
    Inherits from User and hardcodes the MANAGER role via super().__init__().
    Managers have MANAGE_PRODUCTS and MANAGE_USERS permissions.
    """

    def __init__(
            self,
            user_id: int,
            username: str,
            full_name: str
    ):
        super().__init__(user_id, username, full_name, UserRole.MANAGER)


class Cashier(User):
    """
    Concrete subclass of User for cashier accounts.
    Inherits from User and hardcodes the CASHIER role via super().__init__().
    Cashiers have no administrative permissions and can only process sales.
    """

    def __init__(
            self,
            user_id: int,
            username: str,
            full_name: str
    ):
        super().__init__(user_id, username, full_name, UserRole.CASHIER)
