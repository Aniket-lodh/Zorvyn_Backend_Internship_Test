import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.access_control import require_role
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user. Requires **admin** role."
)
async def create_user(
    data: UserCreate,
    _current_user: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await user_service.create_user(db, data)
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List all users",
    description="Return all users. Requires **admin** role."
)
async def list_users(
    _current_user: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    users = await user_service.get_users(db)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
    description="Return a single user by ID. Requires **admin** role."
)
async def get_user(
    user_id: uuid.UUID,
    _current_user: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await user_service.get_user_by_id(db, user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    description="Partially update a user. Requires **admin** role."
)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    _current_user: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await user_service.update_user(db, user_id, data)
    return UserResponse.model_validate(user)
