from datetime import date, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver, DriverStatus
from app.repositories.base import BaseRepository


class DriverRepository(BaseRepository[Driver]):
    def __init__(self, session: AsyncSession):
        super().__init__(Driver, session)

    async def search(
        self,
        *,
        q: str | None = None,
        status: DriverStatus | None = None,
        department: str | None = None,
        offset: int = 0,
        limit: int = 50,
        order_by: str = "-created_at",
    ) -> tuple[list[Driver], int]:
        query = select(Driver)
        count_query = select(func.count()).select_from(Driver)

        if q:
            pattern = f"%{q}%"
            filt = or_(
                Driver.full_name.ilike(pattern),
                Driver.employee_id.ilike(pattern),
                Driver.phone.ilike(pattern),
                Driver.license_number.ilike(pattern),
            )
            query = query.where(filt)
            count_query = count_query.where(filt)

        if status:
            query = query.where(Driver.status == status)
            count_query = count_query.where(Driver.status == status)
        if department:
            query = query.where(Driver.department == department)
            count_query = count_query.where(Driver.department == department)

        total = (await self.session.execute(count_query)).scalar() or 0

        desc = order_by.startswith("-")
        col_name = order_by.lstrip("-")
        if hasattr(Driver, col_name):
            col = getattr(Driver, col_name)
            query = query.order_by(col.desc() if desc else col.asc())

        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all()), total

    async def get_expiring_licenses(self, days: int = 30) -> list[Driver]:
        deadline = date.today() + timedelta(days=days)
        result = await self.session.execute(
            select(Driver).where(
                Driver.status == DriverStatus.ACTIVE,
                Driver.license_expiry <= deadline,
                Driver.license_expiry >= date.today(),
            )
        )
        return list(result.scalars().all())

    async def get_expiring_medicals(self, days: int = 30) -> list[Driver]:
        deadline = date.today() + timedelta(days=days)
        result = await self.session.execute(
            select(Driver).where(
                Driver.status == DriverStatus.ACTIVE,
                Driver.medical_expiry <= deadline,
                Driver.medical_expiry >= date.today(),
            )
        )
        return list(result.scalars().all())
