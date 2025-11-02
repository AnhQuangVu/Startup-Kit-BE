"""Schemas for Notification API"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class NotificationBase(BaseModel):
    """Base notification schema"""
    content: str
    type: str
    related_entity_id: Optional[int] = None


class NotificationResponse(BaseModel):
    """Response schema for a single notification"""
    id: int
    recipient_id: int
    content: str
    type: str
    related_entity_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Response schema for paginated notification list"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int


class NotificationCountResponse(BaseModel):
    """Response schema for notification counts"""
    total: int
    unread: int


class NotificationUpdate(BaseModel):
    """Schema for updating notification"""
    is_read: Optional[bool] = None


class NotificationMarkAllReadRequest(BaseModel):
    """Schema for marking all notifications as read"""
    pass

