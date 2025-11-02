from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from src.database.core import get_db
from src.database.models import User
from . import schemas

router = APIRouter()


@router.get('/public/users/{user_id}', response_model=schemas.UserPublicProfileRead)
def public_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Public endpoint returning a flattened profile for a user (author) used by frontend profile views.

    Response fields match `UserPublicProfileRead` in `src/users/schemas.py`.
    """
    user = (
        db.query(User)
        .options(selectinload(User.profile))
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prof = getattr(user, 'profile', None)

    avatar = None
    if prof and getattr(prof, 'avatar_url', None):
        avatar = prof.avatar_url
    elif getattr(user, 'avatar_url', None):
        avatar = user.avatar_url

    cover = getattr(user, 'cover_url', None) or ""
    name = getattr(user, 'full_name', None) or ""

    try:
        role_val = getattr(user.role, 'value', str(getattr(user, 'role', None)))
    except Exception:
        role_val = str(getattr(user, 'role', None)) or "Founder"

    bio = getattr(prof, 'bio', None) if prof else ""
    location = getattr(prof, 'location', None) if prof else ""
    website = getattr(prof, 'website_url', None) if prof else ""
    phone = getattr(prof, 'phone', None) if prof else ""
    address = getattr(prof, 'address', None) if prof else ""
    company = getattr(prof, 'company', None) if prof else ""
    facebook = getattr(prof, 'facebook', None) if prof else ""
    linkedin = getattr(prof, 'linkedin', None) if prof else ""

    achievements_raw = getattr(prof, 'achievements', None) if prof else None
    achievements_str = ""
    achievement_links = []
    if isinstance(achievements_raw, list):
        parts = []
        for item in achievements_raw:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                content = item.get('content') or item.get('title') or item.get('name')
                link = item.get('link') or item.get('url')
                if content:
                    parts.append(str(content))
                elif link:
                    parts.append(str(link))
                else:
                    try:
                        parts.append(str(item))
                    except Exception:
                        pass
                if link:
                    achievement_links.append(str(link))
            else:
                try:
                    parts.append(str(item))
                except Exception:
                    pass
        achievements_str = ", ".join([p for p in parts if p])

    pitch_deck_url = getattr(user, 'pitch_deck_url', None) or ""
    startups = getattr(prof, 'startups', None) or []
    goal = getattr(user, 'connect_goal', None) or ""

    return {
        'avatar': avatar or "",
        'cover': cover,
        'name': name,
        'role': role_val,
        'bio': bio,
        'location': location,
        'website': website,
        'phone': phone,
        'address': address,
        'company': company,
        'facebook': facebook,
        'linkedin': linkedin,
        'achievements': achievements_str,
        'achievementLinks': achievement_links,
        'pitch_deck_url': pitch_deck_url,
        'startups': startups,
        'goal': goal,
    }

