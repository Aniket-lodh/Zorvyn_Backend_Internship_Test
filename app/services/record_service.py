import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecord, RecordType
from app.schemas.financial_record import RecordCreate, RecordUpdate
from app.utils.exceptions import NotFoundException


async def create_record(
    db: AsyncSession,
    data: RecordCreate,
    created_by: uuid.UUID,
) -> FinancialRecord:
    record = FinancialRecord(
        amount=data.amount,
        type=data.record_type,
        category=data.category,
        date=data.date,
        notes=data.notes,
        created_by=created_by,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_records(
    db: AsyncSession,
    *, 
    record_type: RecordType | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[FinancialRecord]:
    """Returns financial records with optional filtering and pagination."""
    query = select(FinancialRecord)

    if record_type is not None:
        query = query.where(FinancialRecord.type == record_type)
    if category is not None:
        query = query.where(FinancialRecord.category.ilike(category))
    if start_date is not None:
        query = query.where(FinancialRecord.date >= start_date)
    if end_date is not None:
        query = query.where(FinancialRecord.date <= end_date)

    query = query.order_by(FinancialRecord.date.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_record_by_id(
    db: AsyncSession,
    record_id: uuid.UUID,
) -> FinancialRecord:
    """Returns a single record by ID. Raises NotFoundException if the record does not exist."""
    result = await db.execute(
        select(FinancialRecord).where(FinancialRecord.id == record_id),
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise NotFoundException(detail=f"Record with ID '{record_id}' not found.")
    return record


async def update_record(
    db: AsyncSession,
    record_id: uuid.UUID,
    data: RecordUpdate,
) -> FinancialRecord:
    """Partially update an existing financial record. Raises NotFoundException if the record does not exist. """
    record = await get_record_by_id(db, record_id)

    update_data = data.model_dump(exclude_unset=True, by_alias=True)
    if not update_data:
        return record

    for field, value in update_data.items():
        setattr(record, field, value)

    await db.flush()
    await db.refresh(record)
    return record


async def delete_record(db: AsyncSession, record_id: uuid.UUID) -> None:
    """Delete a financial record by ID. Raises NotFoundException if the record does not exist. """
    record = await get_record_by_id(db, record_id)
    await db.delete(record)
    await db.flush()
