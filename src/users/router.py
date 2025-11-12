from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from src.database.models import User
from src.database.core import get_db
from src.auth.service import get_current_user
from . import schemas, service

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=schemas.UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=schemas.UserRead, status_code=status.HTTP_200_OK)
def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = service.update_user(db=db, current_user=current_user, user_update=user_update)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng hoặc bạn không có quyền cập nhật.")
    return user


@router.get("/mentors", response_model=schemas.MentorListResponse)
def get_mentors(
    page: int = 1,
    limit: int = 12,
    expertise_areas: Optional[str] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Discovery endpoint to list mentors with filters, pagination and sorting.
    
    Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 12)
    - expertise_areas: Comma-separated list (e.g., "AI,Blockchain,Fintech")
    - industry: Filter by industry
    - search: Search by name or company
    - sort_by: Sort field (created_at, full_name)
    - order: Sort order (asc, desc)
    - is_active: Filter active mentors only
    """
    areas = None
    if expertise_areas:
        areas = [a.strip() for a in expertise_areas.split(',') if a.strip()]
    items, total = service.list_mentors(
        db=db, 
        page=page, 
        limit=limit, 
        expertise_areas=areas, 
        industry=industry, 
        search=search, 
        sort_by=sort_by, 
        order=order, 
        is_active=is_active
    )
    return {"items": items, "total": total, "page": page, "limit": limit}

@router.put("/me/password", status_code=status.HTTP_200_OK)
def update_user_password_me(
    password_update: schemas.UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if password_update.new_password != password_update.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    success = service.update_user_password(
        db=db, 
        current_user=current_user, 
        password_update=password_update
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
        
    return {"message": "Password updated successfully"}

@router.delete("/me", status_code=status.HTTP_200_OK)
def deactivate_user_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service.deactivate_user(db=db, current_user=current_user)
