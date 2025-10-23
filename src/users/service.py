from sqlalchemy.orm import Session
from src.core.security import get_password_hash, verify_password
from . import schemas
from src.database.models import User, UserProfile

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
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, current_user: User, user_update: schemas.UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)

    # Special-case avatar_url: proxy to profile.avatar_url
    if 'avatar_url' in update_data:
        avatar_value = update_data.pop('avatar_url')
        if not current_user.profile:
            current_user.profile = UserProfile()
        current_user.profile.avatar_url = avatar_value

    for key, value in update_data.items():
        # First try to set attribute on User (but skip read-only proxy properties)
        if hasattr(current_user, key) and key != 'profile':
            try:
                setattr(current_user, key, value)
                continue
            except Exception:
                # If attribute exists but cannot be set (e.g., read-only property), fall back
                pass

        # Then try to set on profile
        if current_user.profile and hasattr(current_user.profile, key):
            setattr(current_user.profile, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

def update_user_password(db: Session, current_user: User, password_update: schemas.UserPasswordUpdate) -> bool:
    if not verify_password(password_update.current_password, current_user.hashed_password):
        return False

    new_hashed_password = get_password_hash(password_update.new_password)
    current_user.hashed_password = new_hashed_password
    db.add(current_user)
    db.commit()
    
    return True

def deactivate_user(db: Session, current_user: User) -> User:
    if not current_user.is_active:
        return current_user

    current_user.is_active = False
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user