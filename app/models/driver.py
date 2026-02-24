import enum
import uuid

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin, UUIDPrimaryKey


class DriverStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class Driver(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "drivers"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    license_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    license_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    license_expiry: Mapped[str | None] = mapped_column(Date, nullable=True)
    medical_expiry: Mapped[str | None] = mapped_column(Date, nullable=True)
    hire_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    department: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus, name="driver_status"),
        default=DriverStatus.ACTIVE,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assigned_vehicles = relationship("Vehicle", back_populates="assigned_driver", foreign_keys="Vehicle.assigned_driver_id")

    def __repr__(self) -> str:
        return f"<Driver {self.full_name}>"
