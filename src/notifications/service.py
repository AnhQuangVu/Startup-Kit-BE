"""Service layer for Notification management"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Tuple, Optional
from src.database.models import Notification, NotificationType


class NotificationService:
    """Service class for notification operations"""

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False
    ) -> Tuple[List[Notification], int, int]:
        """
        Get paginated notifications for a user

        Args:
            db: Database session
            user_id: ID of the user
            page: Page number
            page_size: Number of items per page
            unread_only: If True, only return unread notifications

        Returns:
            Tuple of (notifications list, total count, unread count)
        """
        query = db.query(Notification).filter(Notification.recipient_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        # Get total count
        total = query.count()

        # Get unread count
        unread_count = db.query(Notification).filter(
            and_(
                Notification.recipient_id == user_id,
                Notification.is_read == False
            )
        ).count()

        # Get paginated results
        notifications = (
            query.order_by(desc(Notification.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return notifications, total, unread_count

    @staticmethod
    def get_notification_count(db: Session, user_id: int) -> dict:
        """
        Get notification counts for a user

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Dictionary with total and unread counts
        """
        total = db.query(Notification).filter(
            Notification.recipient_id == user_id
        ).count()

        unread = db.query(Notification).filter(
            and_(
                Notification.recipient_id == user_id,
                Notification.is_read == False
            )
        ).count()

        return {"total": total, "unread": unread}

    @staticmethod
    def get_notification_by_id(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """
        Get a specific notification by ID

        Args:
            db: Database session
            notification_id: ID of the notification
            user_id: ID of the user (for authorization)

        Returns:
            Notification object or None
        """
        return db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.recipient_id == user_id
            )
        ).first()

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """
        Mark a notification as read

        Args:
            db: Database session
            notification_id: ID of the notification
            user_id: ID of the user (for authorization)

        Returns:
            Updated notification or None
        """
        notification = NotificationService.get_notification_by_id(
            db, notification_id, user_id
        )

        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)

        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """
        Mark all notifications as read for a user

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Number of notifications updated
        """
        count = db.query(Notification).filter(
            and_(
                Notification.recipient_id == user_id,
                Notification.is_read == False
            )
        ).update({"is_read": True})

        db.commit()
        return count

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a specific notification

        Args:
            db: Database session
            notification_id: ID of the notification
            user_id: ID of the user (for authorization)

        Returns:
            True if deleted, False if not found
        """
        notification = NotificationService.get_notification_by_id(
            db, notification_id, user_id
        )

        if notification:
            db.delete(notification)
            db.commit()
            return True

        return False

    @staticmethod
    def delete_all_notifications(db: Session, user_id: int) -> int:
        """
        Delete all notifications for a user

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Number of notifications deleted
        """
        count = db.query(Notification).filter(
            Notification.recipient_id == user_id
        ).delete()

        db.commit()
        return count

    @staticmethod
    def create_notification(
        db: Session,
        recipient_id: int,
        content: str,
        notification_type: NotificationType,
        related_entity_id: Optional[int] = None
    ) -> Notification:
        """
        Create a new notification

        Args:
            db: Database session
            recipient_id: ID of the recipient user
            content: Notification content
            notification_type: Type of notification
            related_entity_id: Optional ID of related entity

        Returns:
            Created notification
        """
        notification = Notification(
            recipient_id=recipient_id,
            content=content,
            type=notification_type,
            related_entity_id=related_entity_id,
            is_read=False
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    # Helper methods for creating specific types of notifications

    @staticmethod
    def notify_new_connection_request(
        db: Session,
        recipient_id: int,
        requester_name: str,
        project_name: str,
        connection_id: int
    ) -> Notification:
        """Create notification for new connection request"""
        content = f"{requester_name} đã gửi yêu cầu kết nối đến dự án '{project_name}' của bạn"
        return NotificationService.create_notification(
            db=db,
            recipient_id=recipient_id,
            content=content,
            notification_type=NotificationType.NEW_CONNECTION_REQUEST,
            related_entity_id=connection_id
        )

    @staticmethod
    def notify_connection_accepted(
        db: Session,
        recipient_id: int,
        accepter_name: str,
        project_name: str,
        connection_id: int
    ) -> Notification:
        """Create notification for accepted connection"""
        content = f"{accepter_name} đã chấp nhận yêu cầu kết nối của bạn với dự án '{project_name}'"
        return NotificationService.create_notification(
            db=db,
            recipient_id=recipient_id,
            content=content,
            notification_type=NotificationType.CONNECTION_ACCEPTED,
            related_entity_id=connection_id
        )

    @staticmethod
    def notify_project_update(
        db: Session,
        recipient_id: int,
        project_name: str,
        update_description: str,
        project_id: int
    ) -> Notification:
        """Create notification for project update"""
        content = f"Dự án '{project_name}' có cập nhật mới: {update_description}"
        return NotificationService.create_notification(
            db=db,
            recipient_id=recipient_id,
            content=content,
            notification_type=NotificationType.PROJECT_UPDATE,
            related_entity_id=project_id
        )

    @staticmethod
    def notify_new_message(
        db: Session,
        recipient_id: int,
        sender_name: str,
        conversation_id: int
    ) -> Notification:
        """Create notification for new message"""
        content = f"{sender_name} đã gửi tin nhắn mới cho bạn"
        return NotificationService.create_notification(
            db=db,
            recipient_id=recipient_id,
            content=content,
            notification_type=NotificationType.NEW_MESSAGE,
            related_entity_id=conversation_id
        )

