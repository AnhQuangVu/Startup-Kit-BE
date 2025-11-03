"""Router for Notification API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.core import get_db
from src.auth.service import get_current_user
from src.database.models import User
from src.notifications.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCountResponse,
    NotificationUpdate,
    NotificationMarkAllReadRequest
)
from src.notifications.service import NotificationService

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="Lấy danh sách thông báo",
    description="Lấy danh sách thông báo của user hiện tại với pagination"
)
def get_notifications(
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng items mỗi trang"),
    unread_only: bool = Query(False, description="Chỉ lấy thông báo chưa đọc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách thông báo của user hiện tại

    - **page**: Trang hiện tại (mặc định: 1)
    - **page_size**: Số lượng items mỗi trang (mặc định: 20, max: 100)
    - **unread_only**: Chỉ lấy thông báo chưa đọc (mặc định: false)
    """
    notifications, total, unread_count = NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        unread_only=unread_only
    )

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count
    )


@router.get(
    "/count",
    response_model=NotificationCountResponse,
    summary="Đếm số lượng thông báo",
    description="Lấy tổng số thông báo và số thông báo chưa đọc"
)
def get_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy số lượng thông báo của user hiện tại

    Returns:
    - **total**: Tổng số thông báo
    - **unread**: Số thông báo chưa đọc
    """
    count_data = NotificationService.get_notification_count(db, current_user.id)
    return NotificationCountResponse(**count_data)


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Lấy chi tiết thông báo",
    description="Lấy thông tin chi tiết của một thông báo"
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết của thông báo

    - **notification_id**: ID của thông báo
    """
    notification = NotificationService.get_notification_by_id(
        db, notification_id, current_user.id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông báo"
        )

    return NotificationResponse.model_validate(notification)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Đánh dấu thông báo đã đọc",
    description="Đánh dấu một thông báo là đã đọc"
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đánh dấu thông báo là đã đọc

    - **notification_id**: ID của thông báo
    """
    notification = NotificationService.mark_as_read(
        db, notification_id, current_user.id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông báo"
        )

    return NotificationResponse.model_validate(notification)


@router.post(
    "/mark-all-read",
    summary="Đánh dấu tất cả đã đọc",
    description="Đánh dấu tất cả thông báo của user là đã đọc"
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đánh dấu tất cả thông báo là đã đọc
    """
    count = NotificationService.mark_all_as_read(db, current_user.id)

    return {
        "message": "Đã đánh dấu tất cả thông báo là đã đọc",
        "updated_count": count
    }


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa thông báo",
    description="Xóa một thông báo"
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa thông báo

    - **notification_id**: ID của thông báo
    """
    success = NotificationService.delete_notification(
        db, notification_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông báo"
        )

    return {"message": "Đã xóa thông báo thành công"}


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Xóa tất cả thông báo",
    description="Xóa tất cả thông báo của user"
)
def delete_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa tất cả thông báo của user hiện tại
    """
    count = NotificationService.delete_all_notifications(db, current_user.id)

    return {
        "message": "Đã xóa tất cả thông báo",
        "deleted_count": count
    }

