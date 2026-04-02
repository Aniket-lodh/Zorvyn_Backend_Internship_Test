import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.exceptions import ConflictException, NotFoundException


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """Create a new user. Raises ConflictException if the email already exists. """
    user = User(
        name=data.name,
        email=data.email,
        role=data.role,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail=f"A user with email '{data.email}' already exists.")

    await db.refresh(user)
    return user


async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Return a single user by ID. Raises NotFoundException if the user does not exist. """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException(detail=f"User with ID '{user_id}' not found.")
    return user


async def update_user(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate) -> User:
    """Partially update an existing user.

    Raises NotFoundException if the user does not exist.
    Raises ConflictException if the new email conflicts with another user.
    """
    user = await get_user_by_id(db, user_id)

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return user

    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail=f"A user with email '{data.email}' already exists.",
        )

    await db.refresh(user)
    return user
