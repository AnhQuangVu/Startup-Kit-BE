from pydantic import BaseModel, EmailStr
from typing import Optional
from src.database.models import UserRole
from src.users import schemas as user_schemas

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[user_schemas.UserRead] = None

class TokenData(BaseModel):
    email: str | None = None

class SocialAuthRequest(BaseModel):
    provider: str = "google"  # "google" or "linkedin"
    token: Optional[str] = None  # Google id_token or OAuth access_token
    code: Optional[str] = None   # OAuth authorization code
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = UserRole.FOUNDER
