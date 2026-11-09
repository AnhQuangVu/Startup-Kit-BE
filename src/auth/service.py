import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
import httpx
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.security import get_password_hash
from src.database.core import get_db
from src.database.models import User, UserProfile, UserRole
from src.users import service as user_service
from . import schemas

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = user_service.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """Dependency that returns current user if token valid, otherwise returns None.
    Use this for endpoints that allow anonymous access but should attach user when available.
    """
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except Exception:
        return None


def verify_google_token(token: str) -> Optional[dict]:
    """Verify Google ID token or Access Token and extract user profile."""
    if not token:
        return None
    
    # 1. Try Google ID token validation via tokeninfo
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("email"):
                    return {
                        "email": data.get("email"),
                        "full_name": data.get("name") or data.get("given_name") or data.get("email", "").split("@")[0],
                        "avatar_url": data.get("picture"),
                    }
    except Exception as e:
        logger.warning("Google ID token verification failed: %s", e)

    # 2. Try Google userinfo via Access token Bearer
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("email"):
                    return {
                        "email": data.get("email"),
                        "full_name": data.get("name") or data.get("email", "").split("@")[0],
                        "avatar_url": data.get("picture"),
                    }
    except Exception as e:
        logger.warning("Google access token verification failed: %s", e)

    return None


def verify_linkedin_token(token: str) -> Optional[dict]:
    """Verify LinkedIn Access Token and extract user profile."""
    if not token:
        return None
    try:
        with httpx.Client(timeout=5.0) as client:
            # OpenID Connect userinfo endpoint for LinkedIn
            resp = client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                email = data.get("email")
                name = data.get("name") or f"{data.get('given_name', '')} {data.get('family_name', '')}".strip()
                avatar = data.get("picture")
                return {
                    "email": email,
                    "full_name": name or (email.split("@")[0] if email else "LinkedIn User"),
                    "avatar_url": avatar,
                }
    except Exception as e:
        logger.warning("LinkedIn token verification failed: %s", e)

    return None


def authenticate_or_register_social_user(
    db: Session,
    request: schemas.SocialAuthRequest
) -> Tuple[User, str]:
    """Handles social authentication:
    - Resolves user profile from token or provided social data.
    - If user exists by email, authenticates and updates profile.
    - If user does not exist, registers new user with assigned role.
    - Issues and returns (user, access_token).
    """
    resolved_email: Optional[str] = None
    resolved_name: Optional[str] = None
    resolved_avatar: Optional[str] = None

    provider = (request.provider or "google").lower()

    # 1. Attempt token verification if token provided
    if request.token:
        if provider == "google":
            verified = verify_google_token(request.token)
            if verified:
                resolved_email = verified.get("email")
                resolved_name = verified.get("full_name")
                resolved_avatar = verified.get("avatar_url")
        elif provider == "linkedin":
            verified = verify_linkedin_token(request.token)
            if verified:
                resolved_email = verified.get("email")
                resolved_name = verified.get("full_name")
                resolved_avatar = verified.get("avatar_url")

    # 2. Fall back to user-provided fields if token verification is offline or user passed profile data
    if not resolved_email and request.email:
        resolved_email = str(request.email)
    if not resolved_name and request.full_name:
        resolved_name = request.full_name
    if not resolved_avatar and request.avatar_url:
        resolved_avatar = request.avatar_url

    if not resolved_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể xác thực email từ tài khoản {provider.title()}. Vui lòng thử lại hoặc cung cấp email."
        )

    resolved_email = resolved_email.strip().lower()
    if not resolved_name or not resolved_name.strip():
        resolved_name = resolved_email.split("@")[0].capitalize()
    else:
        resolved_name = resolved_name.strip()

    # 3. Lookup user in database
    user = user_service.get_user_by_email(db, email=resolved_email)

    if user:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên."
            )
        # Update avatar or linkedin if missing
        if resolved_avatar and not user.avatar_url:
            if not user.profile:
                user.profile = UserProfile(user_id=user.id, avatar_url=resolved_avatar)
                db.add(user.profile)
            else:
                user.profile.avatar_url = resolved_avatar
            db.commit()
            db.refresh(user)
    else:
        # 4. Register new user
        role = request.role or UserRole.FOUNDER
        random_pass = secrets.token_urlsafe(32)
        hashed_pwd = get_password_hash(random_pass)

        user = User(
            full_name=resolved_name,
            email=resolved_email,
            hashed_password=hashed_pwd,
            role=role,
            is_active=True
        )
        profile = UserProfile(
            avatar_url=resolved_avatar,
            linkedin=f"https://www.linkedin.com/in/{resolved_email.split('@')[0]}" if provider == "linkedin" else None
        )
        user.profile = profile

        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception as e:
            logger.exception("Failed to create social user: %s", e)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể tạo tài khoản người dùng từ thông tin mạng xã hội."
            )

    # 5. Issue JWT access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return user, access_token
