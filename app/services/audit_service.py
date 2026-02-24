from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction, AuditLog


class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        *,
        user_id: UUID | None,
        action: AuditAction,
        entity_type: str,
        entity_id: UUID | None = None,
        changes: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list_logs(
        self,
        *,
        user_id: UUID | None = None,
        action: AuditAction | None = None,
        entity_type: str | None = None,
        page: int = 1,
        size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        query = select(AuditLog)
        count_query = select(func.count()).select_from(AuditLog)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
            count_query = count_query.where(AuditLog.entity_type == entity_type)

        total = (await self.session.execute(count_query)).scalar() or 0
        result = await self.session.execute(
            query.order_by(AuditLog.timestamp.desc()).offset((page - 1) * size).limit(size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    def compute_diff(old: dict, new: dict) -> dict:
        changes = {}
        for key in set(list(old.keys()) + list(new.keys())):
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val}
        return changes
