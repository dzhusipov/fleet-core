from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.driver import DriverStatus


class DriverCreate(BaseModel):
    full_name: str = Field(..., max_length=255)
    employee_id: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=255)
    license_number: str | None = Field(None, max_length=50)
    license_category: str | None = Field(None, max_length=20)
    license_expiry: date | None = None
    medical_expiry: date | None = None
    hire_date: date | None = None
    department: str | None = None
    status: DriverStatus = DriverStatus.ACTIVE
    user_id: UUID | None = None
    notes: str | None = None


class DriverUpdate(BaseModel):
    full_name: str | None = None
    employee_id: str | None = None
    phone: str | None = None
    email: str | None = None
    license_number: str | None = None
    license_category: str | None = None
    license_expiry: date | None = None
    medical_expiry: date | None = None
    hire_date: date | None = None
    department: str | None = None
    status: DriverStatus | None = None
    notes: str | None = None


class DriverRead(BaseModel):
    id: UUID
    user_id: UUID | None
    full_name: str
    employee_id: str | None
    phone: str | None
    email: str | None
    license_number: str | None
    license_category: str | None
    license_expiry: date | None
    medical_expiry: date | None
    hire_date: date | None
    department: str | None
    status: DriverStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
