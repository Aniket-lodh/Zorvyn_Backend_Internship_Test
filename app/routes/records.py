import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.access_control import require_role
from app.models.financial_record import RecordType
from app.schemas.financial_record import RecordCreate, RecordResponse, RecordUpdate
from app.services import record_service

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post(
    "",
    response_model=RecordResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Create a financial record",
    description="Create a new financial record. Requires **admin** role. The record is automatically linked to the user making the request."
)
async def create_record(
    data: RecordCreate,
    current_user: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> RecordResponse:
    record = await record_service.create_record(db, data, current_user["user_id"])
    return RecordResponse.model_validate(record)


@router.get(
    "",
    response_model=list[RecordResponse],
    response_model_by_alias=True,
    summary="List financial records",
    description="Return financial records with optional filters. Requires **analyst** or **admin** role."
)
async def list_records(
    record_type: RecordType | None = Query(
        default=None, alias="type", description="Filter by record type"
    ),
    category: str | None = Query(default=None, description="Filter by category"),
    start_date: date | None = Query(
        default=None, description="Records on or after this date"
    ),
    end_date: date | None = Query(
        default=None, description="Records on or before this date"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Max number of records"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    _current_user: dict = Depends(require_role(["analyst", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> list[RecordResponse]:
    records = await record_service.get_records(
        db,
        record_type=record_type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return [RecordResponse.model_validate(r) for r in records]


@router.get(
    "/{record_id}",
    response_model=RecordResponse,
    response_model_by_alias=True,
    summary="Get a financial record by ID",
    description="Return a single financial record. Requires **analyst** or **admin** role."
)
async def get_record(
    record_id: uuid.UUID,
    _current_user: dict = Depends(require_role(["analyst", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> RecordResponse:
    record = await record_service.get_record_by_id(db, record_id)
    return RecordResponse.model_validate(record)


@router.patch(
    "/{record_id}",
    response_model=RecordResponse,
    response_model_by_alias=True,
    summary="Update a financial record",
    description="Partially update a financial record. Requires **admin** role."
)
async def update_record(
    record_id: uuid.UUID,
    data: RecordUpdate,
    _current_user: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> RecordResponse:
    record = await record_service.update_record(db, record_id, data)
    return RecordResponse.model_validate(record)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a financial record",
    description="Delete a financial record. Requires **admin** role."
)
async def delete_record(
    record_id: uuid.UUID,
    _current_user: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    await record_service.delete_record(db, record_id)
