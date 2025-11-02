from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from src.database.models import UserRole


class UserProfileBase(BaseModel):
    # avatar_url removed from profile to avoid duplication with top-level User.avatar_url
    bio: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None

class UserProfileRead(UserProfileBase):
    user_id: int
    # new flexible fields
    achievements: Optional[List[Dict[str, Optional[str]]]] = None
    startups: Optional[List[Dict[str, Optional[Any]]]] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):  # Đăng ký người dùng
    full_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    password_confirm: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None
    avatar_url: Optional[str] = None

class UserRead(BaseModel):  # Đọc thông tin người dùng
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    # NOTE: move contact fields into profile to avoid duplication; keep only avatar_url here if you want
    avatar_url: Optional[str] = None
    profile: UserProfileRead

    # New user-level fields
    cover_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None
    connect_goal: Optional[str] = None

    class Config:
        from_attributes = True
        
class UserUpdate(BaseModel):  # Cập nhật thông tin người dùng
    full_name: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None
    # new user-level fields
    cover_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None
    connect_goal: Optional[str] = None
    # new profile-level flexible fields
    achievements: Optional[List[Dict[str, Optional[str]]]] = None
    startups: Optional[List[Dict[str, Optional[Any]]]] = None

class UserPasswordUpdate(BaseModel):  # Cập nhật mật khẩu
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=72)
    new_password_confirm: str

# Public-facing profile schema used by frontend when viewing an author's profile
class UserPublicProfileRead(BaseModel):
    avatar: Optional[str] = None
    cover: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None
    achievements: Optional[str] = None  # joined string for display
    achievementLinks: Optional[List[str]] = None
    pitch_deck_url: Optional[str] = None
    startups: Optional[Any] = None
    goal: Optional[str] = None

    class Config:
        from_attributes = True
