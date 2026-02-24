"""Notification service for in-app, email, and telegram notifications."""

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationPreference, NotificationType
from app.models.user import User


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: NotificationType,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
    ) -> Notification:
        """Create an in-app notification."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        return result.scalar() or 0

    async def get_notifications(
        self, user_id: UUID, limit: int = 20, include_read: bool = False
    ) -> list[Notification]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)
        if not include_read:
            query = query.where(Notification.is_read == False)
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Mark a notification as read."""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(is_read=True)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user."""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )
        await self.db.commit()
        return result.rowcount

    async def get_preferences(self, user_id: UUID) -> NotificationPreference | None:
        """Get notification preferences for a user."""
        result = await self.db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_preferences(
        self,
        user_id: UUID,
        email_enabled: bool | None = None,
        telegram_enabled: bool | None = None,
        telegram_chat_id: str | None = None,
    ) -> NotificationPreference:
        """Create or update notification preferences."""
        pref = await self.get_preferences(user_id)
        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.db.add(pref)

        if email_enabled is not None:
            pref.email_enabled = email_enabled
        if telegram_enabled is not None:
            pref.telegram_enabled = telegram_enabled
        if telegram_chat_id is not None:
            pref.telegram_chat_id = telegram_chat_id

        await self.db.commit()
        await self.db.refresh(pref)
        return pref

    async def notify_fleet_managers(
        self,
        title: str,
        message: str,
        notification_type: NotificationType,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
    ) -> int:
        """Send notification to all fleet managers and admins."""
        from app.models.user import UserRole

        result = await self.db.execute(
            select(User.id).where(
                User.is_active == True,
                User.role.in_([UserRole.ADMIN, UserRole.FLEET_MANAGER]),
            )
        )
        user_ids = [row[0] for row in result.all()]
        count = 0
        for uid in user_ids:
            await self.create_notification(
                user_id=uid,
                title=title,
                message=message,
                notification_type=notification_type,
                entity_type=entity_type,
                entity_id=entity_id,
            )
            count += 1
        return count
