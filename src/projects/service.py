from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session, load_only, selectinload
from . import schemas
from src.database.models import User, Project, ProjectSection
from pydantic import BaseModel
from datetime import datetime, date
import decimal


# List of Project model attributes we will map from incoming payload
PROJECT_SIMPLE_FIELDS = [
    'name', 'tagline', 'description', 'stage', 'website_url', 'profile_url',
    'industry', 'pain_point', 'solution', 'product', 'customer_segment', 'customer_features',
    'market_size', 'market_area', 'deployment_location', 'business_model', 'revenue_method',
    'distribution_channel', 'partners', 'cost_estimate', 'capital_source', 'revenue_goal',
    'member_count', 'member_skills', 'resources', 'use_ai', 'current_stage', 'current_stage_label'
]


def sanitize_for_json(obj: Any) -> Any:
    """Recursively convert objects to JSON-serializable types, coercing values to strings.
    - None -> None (preserve null)
    - str -> str
    - BaseModel -> dict -> sanitized
    - dict -> recursively sanitize keys (keep) and values (as strings or nested)
    - list/tuple/set -> list of sanitized items
    - datetime/date/decimal/number/bool -> string
    - other types -> string via str()

    The user's request: store parameters as strings where reasonable.
    """
    if obj is None:
        return None
    # Keep strings as-is
    if isinstance(obj, str):
        return obj
    # Pydantic models -> dict
    if isinstance(obj, BaseModel):
        return sanitize_for_json(obj.dict())
    # dict -> sanitize values recursively
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new[k] = sanitize_for_json(v)
        return new
    # list/tuple/set -> list
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v) for v in obj]
    # datetime/date/decimal/number/bool/enum/HttpUrl -> coerce to string
    try:
        # datetime/date
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, (int, float, bool)):
            return str(obj)
    except Exception:
        pass
    # fallback: stringify anything else (including HttpUrl)
    try:
        return str(obj)
    except Exception:
        return obj


def _serialize_stage(stage_enum):
    if stage_enum is None:
        return None
    # enum -> value if available
    try:
        return getattr(stage_enum, 'value', str(stage_enum))
    except Exception:
        return str(stage_enum)


def _project_to_response(p: Project) -> Dict[str, Any]:
    # Build base response dict copying columns
    resp: Dict[str, Any] = {
        'id': p.id,
        'founder_id': p.founder_id,
        'name': p.name,
        'tagline': p.tagline,
        'stage': _serialize_stage(p.stage),
        'description': p.description,
        'logo': p.logo,
        'logo_url': p.logo_url,
        'team_image': p.team_image,
        'product_images': p.product_images,
        'website_url': p.website_url,
        'profile_url': p.profile_url,
        'industry': p.industry,
        'pain_point': p.pain_point,
        'solution': p.solution,
        'product': p.product,
        'customer_segment': p.customer_segment,
        'customer_features': p.customer_features,
        'market_size': p.market_size,
        'market_area': p.market_area,
        'business_model': p.business_model,
        'revenue_method': p.revenue_method,
        'distribution_channel': p.distribution_channel,
        'partners': p.partners,
        'cost_estimate': p.cost_estimate,
        'capital_source': p.capital_source,
        'revenue_goal': p.revenue_goal,
        'member_count': p.member_count,
        'member_skills': p.member_skills,
        'resources': p.resources,
        'deployment_location': p.deployment_location,
        'use_ai': p.use_ai,
        'stages': p.stages,
        'current_stage': p.current_stage,
        'current_stage_label': p.current_stage_label,
        'meta': p.meta,
        'created_at': p.created_at,
        'updated_at': p.updated_at,
    }

    # Build sections mapping: original key stored in content['_key'] when available
    sections_map: Dict[str, Any] = {}
    for s in getattr(p, 'sections', []) or []:
        content = s.content
        key = None
        if isinstance(content, dict) and '_key' in content:
            key = content.get('_key')
            # if we wrapped value under 'value', return that
            if 'value' in content and len(content) == 2:
                val = content.get('value')
            else:
                # remove internal _key when exposing
                cpy = dict(content)
                cpy.pop('_key', None)
                val = cpy
        else:
            # fallback key: use title lowercased with underscores
            key = s.title.lower().replace(' ', '_')
            val = content
        # sanitize values for response
        sections_map[key] = sanitize_for_json(val)

    resp['sections'] = sections_map
    return resp


def project_to_response(p: Project) -> Dict[str, Any]:
    # Build base response dict copying columns
    resp: Dict[str, Any] = {
        'id': p.id,
        'founder_id': p.founder_id,
        'name': p.name,
        'tagline': p.tagline,
        'stage': _serialize_stage(p.stage),
        'description': p.description,
        'logo': p.logo,
        'logo_url': p.logo_url,
        'team_image': p.team_image,
        'product_images': p.product_images,
        'website_url': p.website_url,
        'profile_url': p.profile_url,
        'industry': p.industry,
        'pain_point': p.pain_point,
        'solution': p.solution,
        'product': p.product,
        'customer_segment': p.customer_segment,
        'customer_features': p.customer_features,
        'market_size': p.market_size,
        'market_area': p.market_area,
        'business_model': p.business_model,
        'revenue_method': p.revenue_method,
        'distribution_channel': p.distribution_channel,
        'partners': p.partners,
        'cost_estimate': p.cost_estimate,
        'capital_source': p.capital_source,
        'revenue_goal': p.revenue_goal,
        'member_count': p.member_count,
        'member_skills': p.member_skills,
        'resources': p.resources,
        'deployment_location': p.deployment_location,
        'use_ai': p.use_ai,
        'stages': p.stages,
        'current_stage': p.current_stage,
        'current_stage_label': p.current_stage_label,
        'meta': p.meta,
        'created_at': p.created_at,
        'updated_at': p.updated_at,
    }

    # Build sections mapping: original key stored in content['_key'] when available
    sections_map: Dict[str, Any] = {}
    for s in getattr(p, 'sections', []) or []:
        content = s.content
        key = None
        if isinstance(content, dict) and '_key' in content:
            key = content.get('_key')
            # if we wrapped value under 'value', return that
            if 'value' in content and len(content) == 2:
                val = content.get('value')
            else:
                # remove internal _key when exposing
                cpy = dict(content)
                cpy.pop('_key', None)
                val = cpy
        else:
            # fallback key: use title lowercased with underscores
            key = s.title.lower().replace(' ', '_')
            val = content
        # sanitize values for response
        sections_map[key] = sanitize_for_json(val)

    resp['sections'] = sections_map
    return resp


def create_project(db: Session, founder: User, project_data: schemas.ProjectCreate) -> Dict[str, Any]:
    # create base project with minimal required fields
    db_project = Project(
        name=project_data.name,
        tagline=project_data.tagline,
        founder_id=founder.id
    )

    # Map simple scalar fields if present
    for field in PROJECT_SIMPLE_FIELDS:
        if hasattr(project_data, field):
            val = getattr(project_data, field)
            if val is not None:
                # special-case booleans and integers so SQLAlchemy/BOM types accept them
                if field == 'use_ai':
                    # accept bool or string-like values
                    if isinstance(val, bool):
                        db_val = val
                    else:
                        sval = str(val).strip().lower()
                        db_val = sval in ('true', '1', 'yes', 'y', 't')
                    setattr(db_project, field, db_val)
                elif field == 'member_count':
                    try:
                        intval = int(val)
                    except Exception:
                        intval = None
                    setattr(db_project, field, intval)
                else:
                    # sanitize values before assigning to JSON/text columns
                    setattr(db_project, field, sanitize_for_json(val))

    # Media fields (store as JSON objects)
    if getattr(project_data, 'logo', None):
        # ProjectCreate.logo may be a MediaRef or dict; normalize
        logo = project_data.logo.dict() if hasattr(project_data.logo, 'dict') else project_data.logo
        db_project.logo = sanitize_for_json(logo)
        if isinstance(logo, dict) and logo.get('url'):
            db_project.logo_url = str(logo.get('url'))

    if getattr(project_data, 'team_image', None):
        ti = project_data.team_image.dict() if hasattr(project_data.team_image, 'dict') else project_data.team_image
        db_project.team_image = sanitize_for_json(ti)

    if getattr(project_data, 'product_images', None):
        imgs = []
        for p in project_data.product_images:
            if p is None:
                continue
            if hasattr(p, 'dict'):
                imgs.append(sanitize_for_json(p.dict()))
            elif isinstance(p, dict):
                imgs.append(sanitize_for_json(p))
            else:
                imgs.append(sanitize_for_json(p))
        if imgs:
            db_project.product_images = imgs

    # stages and meta
    if getattr(project_data, 'stages', None) is not None:
        db_project.stages = sanitize_for_json([s.dict() if hasattr(s, 'dict') else s for s in project_data.stages])
    if getattr(project_data, 'meta', None) is not None:
        db_project.meta = sanitize_for_json(project_data.meta)

    # Final coercion: ensure boolean/integer columns have correct Python types before DB insert
    # coerce use_ai
    if hasattr(db_project, 'use_ai'):
        val = getattr(db_project, 'use_ai')
        if val is None:
            pass
        elif isinstance(val, bool):
            pass
        elif isinstance(val, (int, float)):
            setattr(db_project, 'use_ai', bool(val))
        else:
            sval = str(val).strip().lower()
            setattr(db_project, 'use_ai', sval in ('true', '1', 'yes', 'y', 't'))

    # coerce member_count
    if hasattr(db_project, 'member_count'):
        mv = getattr(db_project, 'member_count')
        if mv is None:
            pass
        elif isinstance(mv, int):
            pass
        else:
            try:
                intval = int(mv)
            except Exception:
                intval = None
            setattr(db_project, 'member_count', intval)

    db.add(db_project)
    db.flush()  # get db_project.id for sections

    # Persist sections: either provided in project_data.sections (dict) or default sections
    provided_sections = getattr(project_data, 'sections', None)

    if provided_sections and isinstance(provided_sections, dict) and provided_sections:
        # create one ProjectSection per key in the provided sections object
        for key, value in provided_sections.items():
            # normalize key into a type/title
            sec_type = str(key).upper()
            title = str(key)

            content = value
            # If the incoming value is a primitive (str/int), wrap it for consistency
            if not isinstance(content, (dict, list)):
                wrapped = {"_key": key, "value": sanitize_for_json(content)}
            else:
                # if dict/list: sanitize recursively, and include _key
                if isinstance(content, dict):
                    inner = sanitize_for_json(content)
                    wrapped = {"_key": key, **inner}
                else:
                    wrapped = {"_key": key, "value": sanitize_for_json(content)}

            section = ProjectSection(
                project_id=db_project.id,
                type=sec_type,
                title=title,
                content=wrapped
            )
            db.add(section)
    else:
        # create default sections when none provided
        default_sections = [
            {"type": "PITCH_DECK", "title": "Pitch Deck"},
            {"type": "BUSINESS_MODEL_CANVAS", "title": "Business Model Canvas (BMC)"},
            {"type": "MARKET_RESEARCH", "title": "Nghiên cứu thị trường"},
            {"type": "GTM_STRATEGY", "title": "Chiến lược Go-to-Market"},
            {"type": "FINANCIAL_PLAN", "title": "Kế hoạch tài chính"},
        ]

        for section_info in default_sections:
            section = ProjectSection(
                project_id=db_project.id,
                type=section_info["type"],
                title=section_info["title"],
                content={"_key": section_info["type"], "value": {}}
            )
            db.add(section)

    db.commit()

    # Re-query the created project and eager-load sections
    created = (
        db.query(Project)
        .options(selectinload(Project.sections))
        .filter(Project.id == db_project.id)
        .first()
    )

    return _project_to_response(created)


def get_project_by_id(db: Session, project_id: int, user: User) -> Optional[Dict[str, Any]]:
    project = (
        db.query(Project)
        .options(selectinload(Project.sections))
        .filter((Project.id == project_id) & (Project.founder_id == user.id))
        .first()
    )
    if not project:
        return None
    return _project_to_response(project)


def get_projects_by_founder(db: Session, founder_id: int) -> List[Dict[str, Any]]:
    projects = (
        db.query(Project)
        .options(selectinload(Project.sections))
        .filter((Project.founder_id == founder_id))
        .order_by(Project.created_at.desc())
        .all()
    )
    return [_project_to_response(p) for p in projects]


def get_project_section_by_id(db: Session, section_id: int, user: User) -> Optional[ProjectSection]:
    return db.query(ProjectSection).join(Project).filter((ProjectSection.id == section_id) & (Project.founder_id == user.id)).first()


def update_project_section(db: Session, section: ProjectSection,
                           update_data: schemas.ProjectSectionUpdateWS) -> ProjectSection:
    if update_data.title is not None:
        section.title = update_data.title
    if update_data.content is not None:
        section.content = update_data.content

    db.add(section)
    db.commit()
    db.refresh(section)
    return section


from src.database.models import (
    ProjectMember, ProjectPost, PostMedia, PostLike, PostComment, ProjectFollower, Media, ActivityLog
)


def add_project_member(db: Session, project_id: int, member_data: schemas.ProjectMemberCreate, added_by: Optional[User] = None):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    pm = ProjectMember(
        project_id=project_id,
        user_id=getattr(member_data, 'user_id', None),
        name=getattr(member_data, 'name', None),
        avatar_url=str(getattr(member_data, 'avatar_url', None)) if getattr(member_data, 'avatar_url', None) else None,
        role_in_project=getattr(member_data, 'role_in_project', None),
        is_founder=getattr(member_data, 'is_founder', False)
    )
    db.add(pm)
    db.commit()
    db.refresh(pm)
    # activity
    try:
        db.add(ActivityLog(project_id=project_id, actor_id=(added_by.id if added_by else None), type='member_added', payload={'member_id': pm.id}))
        db.commit()
    except Exception:
        db.rollback()
    return pm


def get_project_members(db: Session, project_id: int):
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).order_by(ProjectMember.joined_at.asc()).all()


def create_project_post(db: Session, project_id: int, author: User, post_data: schemas.ProjectPostCreate):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    post = ProjectPost(
        project_id=project_id,
        author_id=(author.id if author else None),
        title=getattr(post_data, 'title', None),
        body=getattr(post_data, 'body', None),
        visibility=getattr(post_data, 'visibility', 'public')
    )
    db.add(post)
    db.flush()

    # media
    medias = getattr(post_data, 'media', None) or []
    for idx, m in enumerate(medias):
        url = m.url if hasattr(m, 'url') else m.get('url')
        pm = PostMedia(post_id=post.id, url=str(url), public_id=getattr(m, 'public_id', None), media_type=getattr(m, 'media_type', None), order=idx)
        db.add(pm)

    db.commit()
    db.refresh(post)

    # log
    try:
        db.add(ActivityLog(project_id=project_id, actor_id=(author.id if author else None), type='post_created', payload={'post_id': post.id}))
        db.commit()
    except Exception:
        db.rollback()

    # Re-query the post with author relationship loaded so Pydantic can access author fields
    from src.database.models import ProjectPost as _PP
    post_with_author = (
        db.query(_PP)
        .options(selectinload(_PP.author), selectinload(_PP.media))
        .filter(_PP.id == post.id)
        .first()
    )

    return post_with_author


def get_project_posts(db: Session, project_id: int, limit: int = 50):
    return (
        db.query(ProjectPost)
        .options(selectinload(ProjectPost.author), selectinload(ProjectPost.media))
        .filter(ProjectPost.project_id == project_id)
        .order_by(ProjectPost.created_at.desc())
        .limit(limit)
        .all()
    )


def get_post_by_id(db: Session, post_id: int):
    return (
        db.query(ProjectPost)
        .options(selectinload(ProjectPost.author), selectinload(ProjectPost.media))
        .filter(ProjectPost.id == post_id)
        .first()
    )


def add_comment_to_post(db: Session, post_id: int, author: User, comment_data: schemas.PostCommentCreate):
    post = get_post_by_id(db, post_id=post_id)
    if not post:
        raise ValueError("Post not found")
    parent_id = getattr(comment_data, 'parent_comment_id', None)
    # If parent_id provided, validate it exists and belongs to same post
    if parent_id is not None:
        parent = db.query(PostComment).filter(PostComment.id == parent_id).first()
        if not parent:
            raise ValueError("Parent comment not found")
        if parent.post_id != post_id:
            raise ValueError("Parent comment must belong to the same post")

    pc = PostComment(post_id=post_id, author_id=(author.id if author else None), body=comment_data.body, parent_comment_id=parent_id)
    db.add(pc)
    db.commit()
    db.refresh(pc)
    try:
        db.add(ActivityLog(project_id=post.project_id, actor_id=(author.id if author else None), type='comment_created', payload={'post_id': post_id, 'comment_id': pc.id}))
        db.commit()
    except Exception:
        db.rollback()

    # Re-query the created comment with author info so we can return serialized payload
    from src.database.models import PostComment as _PC
    created = (
        db.query(_PC)
        .options(selectinload(_PC.author))
        .filter(_PC.id == pc.id)
        .first()
    )

    def _serialize_comment(c: _PC) -> Dict[str, Any]:
        return {
            'id': c.id,
            'post_id': c.post_id,
            'author_id': c.author_id,
            'author': {
                'id': c.author.id,
                'full_name': c.author.full_name,
                'avatar_url': c.author.avatar_url
            } if getattr(c, 'author', None) else None,
            'body': c.body,
            'parent_comment_id': c.parent_comment_id,
            'created_at': c.created_at,
            'replies': []
        }

    return _serialize_comment(created)


def get_comments_for_post(db: Session, post_id: int):
    """Return comments for a post as a nested list (tree) of dicts with author info."""
    from src.database.models import PostComment as _PC

    comments = (
        db.query(_PC)
        .filter(_PC.post_id == post_id)
        .order_by(_PC.created_at.asc())
        .options(selectinload(_PC.author))
        .all()
    )

    # Map id -> serialized dict
    nodes: Dict[int, Dict[str, Any]] = {}
    roots: List[Dict[str, Any]] = []

    for c in comments:
        nodes[c.id] = {
            'id': c.id,
            'post_id': c.post_id,
            'author_id': c.author_id,
            'author': {
                'id': c.author.id,
                'full_name': c.author.full_name,
                'avatar_url': c.author.avatar_url
            } if getattr(c, 'author', None) else None,
            'body': c.body,
            'parent_comment_id': c.parent_comment_id,
            'created_at': c.created_at,
            'replies': []
        }

    # Build tree
    for c in comments:
        node = nodes[c.id]
        if c.parent_comment_id and c.parent_comment_id in nodes:
            nodes[c.parent_comment_id]['replies'].append(node)
        else:
            roots.append(node)

    return roots


def like_post(db: Session, post_id: int, user: User):
    post = get_post_by_id(db, post_id=post_id)
    if not post:
        raise ValueError("Post not found")
    # prevent duplicate likes
    existing = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == user.id).first()
    if existing:
        return existing
    pl = PostLike(post_id=post_id, user_id=user.id)
    db.add(pl)
    db.commit()
    db.refresh(pl)
    try:
        db.add(ActivityLog(project_id=post.project_id, actor_id=user.id, type='post_liked', payload={'post_id': post_id, 'like_id': pl.id}))
        db.commit()
    except Exception:
        db.rollback()
    return pl


def follow_project(db: Session, project_id: int, user: User):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")
    existing = db.query(ProjectFollower).filter(ProjectFollower.project_id == project_id, ProjectFollower.user_id == user.id).first()
    if existing:
        return existing
    pf = ProjectFollower(project_id=project_id, user_id=user.id)
    db.add(pf)
    db.commit()
    db.refresh(pf)
    # optional: update cached follower_count in Project.meta or column (not present by default)
    try:
        db.add(ActivityLog(project_id=project_id, actor_id=user.id, type='project_followed', payload={'follower_id': pf.id}))
        db.commit()
    except Exception:
        db.rollback()
    return pf


def unfollow_project(db: Session, project_id: int, user: User):
    existing = db.query(ProjectFollower).filter(ProjectFollower.project_id == project_id, ProjectFollower.user_id == user.id).first()
    if not existing:
        return None
    db.delete(existing)
    db.commit()
    try:
        db.add(ActivityLog(project_id=project_id, actor_id=user.id, type='project_unfollowed', payload={'user_id': user.id}))
        db.commit()
    except Exception:
        db.rollback()
    return existing


def get_project_followers(db: Session, project_id: int, limit: int = 100):
    return db.query(ProjectFollower).filter(ProjectFollower.project_id == project_id).order_by(ProjectFollower.created_at.desc()).limit(limit).all()


async def publish_project(db: Session, project_id: int, user_id: int):
    """Publish a project to the platform"""
    project = db.query(Project).filter(Project.id == project_id).first()

    project.status = "published"
    project.published_at = datetime.utcnow()
    project.published_by = user_id

    db.add(project)
    db.commit()
    db.refresh(project)

    # Log activity
    activity = ActivityLog(
        project_id=project_id,
        actor_id=user_id,
        type="project_published"
    )
    db.add(activity)
    db.commit()

    return project


def update_project(db: Session, project_id: int, update_data: schemas.ProjectCreate, user: User):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")
    if project.founder_id != user.id:
        raise ValueError("Only project founder can update")

    # Update simple fields
    for field in PROJECT_SIMPLE_FIELDS:
        if hasattr(update_data, field) and getattr(update_data, field) is not None:
            setattr(project, field, getattr(update_data, field))

    # Update media fields
    if update_data.logo:
        project.logo = update_data.logo.dict() if update_data.logo else None
    if update_data.logo_url:
        project.logo_url = str(update_data.logo_url) if update_data.logo_url else None
    if update_data.team_image:
        project.team_image = update_data.team_image.dict() if update_data.team_image else None
    if update_data.product_images:
        project.product_images = [img.dict() for img in update_data.product_images] if update_data.product_images else None

    # Update stages
    if update_data.stages:
        project.stages = [stage.dict() for stage in update_data.stages]

    # Update meta
    if update_data.meta is not None:
        project.meta = sanitize_for_json(update_data.meta)

    # Update sections
    if update_data.sections is not None:
        # Assuming sections are stored as JSON
        project.sections = sanitize_for_json(update_data.sections)

    project.updated_at = datetime.utcnow()
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_to_response(project)


def delete_project(db: Session, project_id: int, user: User):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")
    if project.founder_id != user.id:
        raise ValueError("Only project founder can delete")

    db.delete(project)
    db.commit()
    return True


def update_post(db: Session, post_id: int, update_data: schemas.ProjectPostCreate, user: User):
    from src.database.models import ProjectPost
    post = db.query(ProjectPost).filter(ProjectPost.id == post_id).first()
    if not post:
        raise ValueError("Post not found")
    if post.author_id != user.id:
        raise ValueError("Only post author can update")

    if update_data.title is not None:
        post.title = update_data.title
    if update_data.body is not None:
        post.body = update_data.body
    if update_data.media is not None:
        # Assuming media is stored as JSON
        post.media = [media.dict() for media in update_data.media]
    if update_data.visibility is not None:
        post.visibility = update_data.visibility

    post.updated_at = datetime.utcnow()
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int, user: User):
    from src.database.models import ProjectPost
    post = db.query(ProjectPost).filter(ProjectPost.id == post_id).first()
    if not post:
        raise ValueError("Post not found")
    if post.author_id != user.id:
        raise ValueError("Only post author can delete")

    db.delete(post)
    db.commit()
    return True


def get_all_projects(db: Session, skip: int = 0, limit: int = 10):
    projects = (
        db.query(Project)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_project_to_response(p) for p in projects]


def get_published_projects(db: Session, skip: int = 0, limit: int = 10):
    projects = (
        db.query(Project)
        .filter(Project.status == "published")
        .order_by(Project.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Return full project responses
    return [_project_to_response(p) for p in projects]


def get_published_projects_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    projects = (
        db.query(Project)
        .filter(Project.status == "published")
        .filter(Project.founder_id == user_id)
        .order_by(Project.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Return full project responses
    return [_project_to_response(p) for p in projects]
