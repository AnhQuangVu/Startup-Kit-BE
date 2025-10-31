from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from src.database.core import get_db
from src.database.models import Project

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
    }


@router.get('/public/projects/published')
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

    # Fetch page
    rows = (
        base_q.order_by(order_clause)
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

