import enum
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, UUIDPrimaryKey


class MileageSource(str, enum.Enum):
    MANUAL = "manual"
    OBD = "obd"
    GPS = "gps"


class MileageLog(Base, UUIDPrimaryKey):
    __tablename__ = "mileage_logs"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recorded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[MileageSource] = mapped_column(
        Enum(MileageSource, name="mileage_source"),
        default=MileageSource.MANUAL,
        nullable=False,
    )
    recorded_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    vehicle = relationship("Vehicle", foreign_keys=[vehicle_id])
    recorder = relationship("User", foreign_keys=[recorded_by])
