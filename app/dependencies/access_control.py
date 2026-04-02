import uuid
from collections.abc import Callable

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.user_service import get_user_by_id
from app.utils.exceptions import BadRequestException, ForbiddenException, NotFoundException, UnauthorizedException


async def get_current_user(
    x_user_id: str = Header(description="User UUID"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Validate identity from header, fetch user from DB, and return identity dict.

    Raises `BadRequestException` if X-User-Id is strictly unparsable as UUID.
    Raises `UnauthorizedException` if user does not exist.
    Raises `ForbiddenException` if the user is inactive.
    """
    try:
        user_uuid = uuid.UUID(x_user_id)
    except ValueError:
        raise BadRequestException(
            detail=f"Invalid user ID '{x_user_id}'. Must be a valid UUID.",
        )

    try:
        user = await get_user_by_id(db, user_uuid)
    except NotFoundException:
        raise UnauthorizedException(detail="User not found")

    if not user.is_active:
        raise ForbiddenException(detail="Inactive user")

    return {"user_id": user.id, "role": user.role}


def require_role(allowed_roles: list[str]) -> Callable:
    """Factory that returns a FastAPI dependency enforcing role-based access.
    Usage in a route:
    ```python
    @router.get("/records")
    async def list_records(
        current_user: dict = Depends(require_role(["analyst","admin"]))
    ):
        ...
    ```
    """


    async def _role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        if current_user["role"] not in allowed_roles:
            raise ForbiddenException(
                detail=f"Role '{current_user['role']}' does not have access. "
                f"Required: {', '.join(allowed_roles)}",
            )

        return current_user

    return _role_checker
