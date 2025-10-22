from typing import Optional
from pydantic.networks import HttpUrl
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
    avatar_url: Optional[HttpUrl] = None

class UserRead(BaseModel):  # Đọc thông tin người dùng
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    # NOTE: move contact fields into profile to avoid duplication; keep only avatar_url here if you want
    avatar_url: Optional[HttpUrl] = None
    profile: UserProfileRead

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

class UserPasswordUpdate(BaseModel):  # Cập nhật mật khẩu
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=72)
    new_password_confirm: str
