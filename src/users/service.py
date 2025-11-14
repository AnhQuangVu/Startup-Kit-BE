from sqlalchemy.orm import Session, joinedload
from src.core.security import get_password_hash, verify_password
from . import schemas
from src.database.models import User, UserProfile, MentorProfile
from sqlalchemy import func, or_, asc, desc
from typing import Optional, List, Tuple
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

    # Handle mentor_profile separately for mentor users
    if 'mentor_profile' in update_data and update_data['mentor_profile'] is not None:
        mentor_data = update_data.pop('mentor_profile')
        
        # Only process if user is a mentor
        if current_user.role.value == 'mentor':
            if not current_user.mentor_profile:
                current_user.mentor_profile = MentorProfile(user_id=current_user.id)
            
            # Update mentor profile fields
            for field, value in mentor_data.items():
                if hasattr(current_user.mentor_profile, field):
                    setattr(current_user.mentor_profile, field, value)

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


def list_mentors(
    db: Session,
    page: Optional[int] = 1,
    limit: Optional[int] = 12,
    expertise_areas: Optional[List[str]] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "desc",
    is_active: Optional[bool] = True,
) -> Tuple[List[dict], int]:
    """List mentors with filters, pagination and sorting.

    Returns: (items, total)
    """
    query = db.query(User).outerjoin(MentorProfile).options(
        joinedload(User.profile), joinedload(User.mentor_profile)
    ).filter(User.role == "mentor")

    # is_active filter (default True)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # expertise_areas: accept list of strings - match any (OR)
    if expertise_areas:
        # try JSON overlap / contains
        try:
            query = query.filter(MentorProfile.expertise_areas.contains(expertise_areas))
        except Exception:
            # fallback - try JSON_OVERLAPS if available
            try:
                query = query.filter(func.JSON_OVERLAPS(MentorProfile.expertise_areas, func.JSON_ARRAY(*[func.json_quote(x) for x in expertise_areas])))
            except Exception:
                pass

    # industry filter if mentor_profile has this field
    if industry and hasattr(MentorProfile, 'industry'):
        query = query.filter(getattr(MentorProfile, 'industry') == industry)

    # search -> full_name OR company (in UserProfile)
    if search:
        term = f"%{search}%"
        query = query.outerjoin(User.profile).filter(
            or_(
                User.full_name.ilike(term),
                UserProfile.company.ilike(term)
            )
        )

    # sorting
    sort_map = {
        'created_at': User.created_at,
        'full_name': User.full_name,
    }
    # support mentor_profile.experience_years if exists
    if hasattr(MentorProfile, 'experience_years'):
        sort_map['experience_years'] = getattr(MentorProfile, 'experience_years')

    sort_col = sort_map.get(sort_by, User.created_at)
    order_fn = asc if order.lower() == 'asc' else desc
    query = query.order_by(order_fn(sort_col))

    # total count
    total = query.order_by(None).count()

    # pagination
    offset = (max(page, 1) - 1) * max(limit, 1)
    users = query.offset(offset).limit(limit).all()

    # build items
    items = []
    for u in users:
        # achievements: use mentor_profile.achievements if present, else profile.achievements
        ach = None
        if getattr(u, 'mentor_profile', None) and getattr(u.mentor_profile, 'achievements', None):
            ach = u.mentor_profile.achievements
        elif getattr(u, 'profile', None) and getattr(u.profile, 'achievements', None):
            ach = u.profile.achievements

        # limit achievements to top 3
        if isinstance(ach, list):
            achievements = ach[:3]
        else:
            achievements = None

        items.append({
            'id': u.id,
            'full_name': u.full_name,
            'avatar_url': u.avatar_url or (u.profile.avatar_url if u.profile else None),
            'cover_url': u.cover_url,
            'bio': (u.profile.bio if u.profile else None),
            'company': (u.profile.company if u.profile else None),
            'mentor_profile': u.mentor_profile,
            'achievements': achievements,
        })

    return items, total