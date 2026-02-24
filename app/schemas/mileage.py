from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.mileage import MileageSource


class MileageCreate(BaseModel):
    vehicle_id: UUID
    value: int = Field(..., ge=0)
    source: MileageSource = MileageSource.MANUAL
    notes: str | None = None


class BulkMileageCreate(BaseModel):
    entries: list[MileageCreate]


class MileageRead(BaseModel):
    id: UUID
    vehicle_id: UUID
    recorded_by: UUID | None
    value: int
    source: MileageSource
    recorded_at: datetime
    notes: str | None

    model_config = {"from_attributes": True}
