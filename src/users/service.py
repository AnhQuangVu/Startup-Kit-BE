from sqlalchemy.orm import Session
from src.core.security import get_password_hash, verify_password
from . import schemas
from src.database.models import User, UserProfile
import logging

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db_user.profile = UserProfile()
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception:
        logger.exception("Failed to create user; rolling back")
        db.rollback()
        raise
    return db_user

def update_user(db: Session, current_user: User, user_update: schemas.UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)

    # Protect certain fields from being updated via this endpoint
    protected_keys = {'id', 'user_id', 'email', 'hashed_password', 'role', 'created_at', 'updated_at'}

    # If any profile-level fields are present, ensure profile exists
    profile_fields = {'avatar_url', 'bio', 'website_url', 'location', 'phone', 'address', 'company', 'facebook', 'linkedin', 'achievements', 'startups'}
    if any(k in profile_fields for k in update_data.keys()) and not current_user.profile:
        current_user.profile = UserProfile()

    # Special-case avatar_url: proxy to profile.avatar_url
    if 'avatar_url' in update_data:
        avatar_value = update_data.pop('avatar_url')
        if not current_user.profile:
            current_user.profile = UserProfile()
        current_user.profile.avatar_url = avatar_value

    for key, value in list(update_data.items()):
        # Skip protected keys
        if key in protected_keys:
            continue

        # First try to set attribute on User (but skip read-only proxy properties)
        if hasattr(current_user, key) and key != 'profile':
            try:
                setattr(current_user, key, value)
                continue
            except Exception:
                # If attribute exists but cannot be set (e.g., read-only property), fall back
                pass

        # Then try to set on profile if attribute exists
        if current_user.profile and hasattr(current_user.profile, key):
            try:
                setattr(current_user.profile, key, value)
                continue
            except Exception:
                pass

        # Fallback: if profile exists and key is one of flexible JSON fields, set it there
        if current_user.profile and key in ('achievements', 'startups'):
            try:
                # ensure values are lists (basic validation) before assigning
                if value is None:
                    setattr(current_user.profile, key, None)
                elif isinstance(value, list):
                    setattr(current_user.profile, key, value)
                else:
                    # ignore invalid types
                    pass
            except Exception:
                pass

    db.add(current_user)
    try:
        db.commit()
        db.refresh(current_user)
    except Exception:
        logger.exception("Failed to update user; rolling back")
        db.rollback()
        raise
    return current_user

def update_user_password(db: Session, current_user: User, password_update: schemas.UserPasswordUpdate) -> bool:
    if not verify_password(password_update.current_password, current_user.hashed_password):
        return False

    new_hashed_password = get_password_hash(password_update.new_password)
    current_user.hashed_password = new_hashed_password
    db.add(current_user)
    try:
        db.commit()
    except Exception:
        logger.exception("Failed to update user password; rolling back")
        db.rollback()
        raise

    return True

def deactivate_user(db: Session, current_user: User) -> User:
    if not current_user.is_active:
        return current_user

    current_user.is_active = False
    db.add(current_user)
    try:
        db.commit()
        db.refresh(current_user)
    except Exception:
        logger.exception("Failed to deactivate user; rolling back")
        db.rollback()
        raise

    return current_user