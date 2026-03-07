from enum import Enum

from constant.enums import UserRole


class Permission(str, Enum):
    MANAGE_PRODUCTS = 'manage_products'
    MANAGE_USERS = 'manage_users'


ROLE_PERMISSIONS = {
    UserRole.MANAGER: {Permission.MANAGE_PRODUCTS, Permission.MANAGE_USERS},
    UserRole.CASHIER: set(),
}


def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if the given user role has the specified permission."""
    return permission in ROLE_PERMISSIONS.get(user_role, set())
