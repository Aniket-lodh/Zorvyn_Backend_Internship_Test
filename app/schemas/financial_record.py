import uuid
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.financial_record import RecordType


class RecordCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: float = Field(gt=0, examples=[1500.00])
    record_type: RecordType = Field(alias="type", examples=["income"])
    category: str = Field(min_length=1, max_length=100, examples=["Salary"])
    date: Date = Field(examples=["2025-01-15"])
    notes: str | None = Field(default=None, max_length=500, examples=["Monthly salary"])

    @field_validator("date")
    @classmethod
    def date_must_not_be_in_future(cls, v: Date) -> Date:
        if v > Date.today():
            raise ValueError("Date cannot be in the future")
        return v


class RecordUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: float | None = Field(default=None, gt=0)
    record_type: RecordType | None = Field(default=None, alias="type")
    category: str | None = Field(default=None, min_length=1, max_length=100)
    date: Date | None = Field(default=None)
    notes: str | None = Field(default=None, max_length=500)


class RecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    amount: float
    record_type: RecordType = Field(alias="type")
    category: str
    date: Date
    notes: str | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
