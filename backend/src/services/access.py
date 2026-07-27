from enum import Enum

from authentication.models import Role


class ServiceAccessLevel(str, Enum):
    """Audience allowed to discover and execute a service."""

    PUBLIC = "public"
    USER = "user"
    ADMIN = "admin"
    DISABLED = "disabled"


def accessible_service_levels(role: Role | None) -> list[ServiceAccessLevel]:
    """Return every service access level visible to a user with ``role``."""

    levels = [ServiceAccessLevel.PUBLIC]
    if role in (Role.USER, Role.ADMIN):
        levels.append(ServiceAccessLevel.USER)
    if role == Role.ADMIN:
        levels.append(ServiceAccessLevel.ADMIN)
    return levels


def can_access_service(access_level: ServiceAccessLevel, role: Role | None) -> bool:
    """Check whether a role may discover or execute a service."""

    return access_level in accessible_service_levels(role)
