from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import selectinload
from src.database.core import get_db
from src.database.models import Project, User
from src.users.schemas import UserPublicProfileRead
from fastapi import HTTPException, Depends
from src.database.core import get_db
from sqlalchemy.orm import Session

router = APIRouter()


def _serialize_project(p: Project) -> dict:
    # Safe-get attributes; fallbacks for status/published
    published_val = None
    if hasattr(p, 'published'):
        published_val = getattr(p, 'published')
    elif hasattr(p, 'status'):
        published_val = getattr(p, 'status') == 'published'
    else:
        published_val = None

    # basic founder info
    founder_obj = None
    try:
        if getattr(p, 'founder', None):
            u = p.founder
            prof = getattr(u, 'profile', None)
            # normalize achievements
            ach = None
            if prof and getattr(prof, 'achievements', None) is not None:
                if isinstance(prof.achievements, list):
                    ach = prof.achievements
                elif isinstance(prof.achievements, str):
                    ach = [a.strip() for a in prof.achievements.split(';') if a.strip()]

            # If we have achievements, normalize items to strings for frontend convenience
            if ach is not None:
                norm_ach = []
                for item in ach:
                    if isinstance(item, str):
                        norm_ach.append(item)
                    elif isinstance(item, dict):
                        # prefer content or link fields, else stringify
                        val = item.get('content') if item.get('content') else (item.get('link') if item.get('link') else None)
                        if val is None:
                            try:
                                norm_ach.append(str(item))
                            except Exception:
                                norm_ach.append('')
                        else:
                            norm_ach.append(str(val))
                    else:
                        try:
                            norm_ach.append(str(item))
                        except Exception:
                            norm_ach.append('')
                ach = norm_ach

            # startups
            su = None
            if prof and getattr(prof, 'startups', None) is not None:
                su = prof.startups

            founder_obj = {
                'id': u.id,
                'avatar': getattr(u, 'avatar_url', None) or (getattr(prof, 'avatar_url', None) if prof else None),
                'cover': getattr(u, 'cover_url', None) or (getattr(prof, 'cover_url', None) if prof else None),
                'name': getattr(u, 'full_name', None),
                'role': getattr(prof, 'role', None) if prof and getattr(prof, 'role', None) else (getattr(u, 'role', None).value if getattr(u, 'role', None) else None),
                'bio': getattr(prof, 'bio', None) if prof else None,
                'location': getattr(prof, 'location', None) if prof else None,
                'website': getattr(prof, 'website_url', None) if prof else None,
                'phone': getattr(prof, 'phone', None) if prof else None,
                'address': getattr(prof, 'address', None) if prof else None,
                'company': getattr(prof, 'company', None) if prof else None,
                'facebook': getattr(prof, 'facebook', None) if prof else None,
                'linkedin': getattr(prof, 'linkedin', None) if prof else None,
                'achievements': ach,
                'pitch_deck_url': getattr(u, 'pitch_deck_url', None) or (getattr(prof, 'pitch_deck_url', None) if prof else None),
                'startups': su,
                'goal': getattr(u, 'connect_goal', None) or (getattr(prof, 'connect_goal', None) if prof else None)
            }
    except Exception:
        founder_obj = None

    return {
        'id': p.id,
        'name': p.name,
        'tagline': p.tagline,
        'description': p.description,
        'industry': p.industry,
        'stage': p.stage,
        'created_at': p.created_at.isoformat() if getattr(p, 'created_at', None) is not None else None,
        'published': published_val,
        'logo_url': p.logo_url,
        'member_count': p.member_count,
        'capital_source': p.capital_source,
        'founder': founder_obj,
    }


@router.get('/public/projects/published', response_model=Dict[str, Any])
def public_published_projects(
    q: Optional[str] = Query(None),
    industry: Optional[List[str]] = Query(None),
    stage: Optional[List[str]] = Query(None),
    sort: str = Query('newest'),
    limit: int = Query(24, gt=0),
    cursor: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Return published projects with search, filters and offset pagination.

    Response JSON: { items: [...], nextCursor: <int or null>, total: <int> }
    """
    # Base query: only published projects
    base_q = db.query(Project)
    if hasattr(Project, 'status'):
        base_q = base_q.filter(Project.status == 'published')
    elif hasattr(Project, 'published'):
        base_q = base_q.filter(getattr(Project, 'published') == True)

    # Filters
    if industry:
        base_q = base_q.filter(Project.industry.in_(industry))
    if stage:
        base_q = base_q.filter(Project.stage.in_(stage))

    # Search q across name, tagline, description (ILIKE compatible)
    if q:
        pattern = f"%{q}%"
        base_q = base_q.filter(
            or_(
                Project.name.ilike(pattern),
                Project.tagline.ilike(pattern),
                Project.description.ilike(pattern),
            )
        )

    # Total count
    try:
        total = base_q.count()
    except Exception:
        # fallback: materialize list and get len
        total = len(base_q.all())

    # Sorting
    if sort == 'oldest':
        order_clause = asc(Project.created_at)
    else:
        order_clause = desc(Project.created_at)

    # Fetch page with eager-load of founder + profile to avoid N+1
    rows = (
        base_q.options(selectinload(Project.founder).selectinload(User.profile))
        .order_by(order_clause)
        .offset(cursor)
        .limit(limit)
        .all()
    )

    items = [_serialize_project(p) for p in rows]

    # nextCursor is offset for next page
    next_cursor = None
    if cursor + limit < total:
        next_cursor = cursor + limit

    return {
        'items': items,
        'nextCursor': next_cursor,
        'total': total,
    }


@router.get('/public/users/{user_id}', response_model=UserPublicProfileRead)
def public_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Public author profile used by frontend setUser(...) mapping.

    Returns fields: avatar, cover, name, role, bio, location, website, phone, address,
    company, facebook, linkedin, achievements (joined string), achievementLinks (list),
    pitch_deck_url, startups (list), goal
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

    avatar = (getattr(prof, 'avatar_url', None) if prof else None) or getattr(user, 'avatar_url', None) or ""
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
        'avatar': avatar,
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
