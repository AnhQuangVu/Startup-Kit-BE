from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query, Request
from sqlalchemy.orm import Session
from typing import List

from src.database.core import get_db
from src.database.models import User
from src.auth.service import get_current_user
from . import schemas, service
from .router_public import router as public_router

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


async def get_current_user_from_token_ws(
        token: str = Query(...),
        db: Session = Depends(get_db)
) -> User:
    user = get_current_user(token=token, db=db)
    return user


@router.post("/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_new_project(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Accept flexible JSON from frontend. Keys that match `ProjectCreate` fields are used as project fields;
    other top-level keys are collected into `sections` and passed to service.create_project.
    Also accepts `profile_meta` as `meta`, top-level `tags`, and `logo`/`team_image`/`product_images` mapping.
    """
    if current_user.role != 'founder':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only founders can create projects."
        )

    payload = await request.json()

    # Determine allowed project fields from the Pydantic model
    if hasattr(schemas.ProjectCreate, 'model_fields'):
        model_fields = set(schemas.ProjectCreate.model_fields.keys())
    else:
        model_fields = set(getattr(schemas.ProjectCreate, '__fields__', {}).keys())

    project_data = {}
    sections = {}
    meta = None

    for k, v in payload.items():
        # accept alternative meta key names
        if k == 'meta' or k in ('profile_meta', 'profileMeta'):
            meta = v
            continue
        if k in model_fields:
            project_data[k] = v
        else:
            sections[k] = v

    # extract from basic if present
    basic = sections.get('basic') if isinstance(sections.get('basic'), dict) else None
    if basic:
        if not project_data.get('name'):
            project_data['name'] = basic.get('name') or basic.get('projectName')
        if 'tagline' in model_fields and not project_data.get('tagline'):
            project_data['tagline'] = basic.get('tagline') or basic.get('subtitle')
        if 'description' in model_fields and not project_data.get('description'):
            project_data['description'] = basic.get('summary') or basic.get('description')
        logo = basic.get('logo')
        if logo and isinstance(logo, dict) and 'logo_url' in model_fields and not project_data.get('logo_url'):
            project_data['logo_url'] = logo.get('url')

    # top-level logo/team_image/product_images mapping
    top_logo = payload.get('logo')
    if top_logo and isinstance(top_logo, dict) and 'logo_url' in model_fields and not project_data.get('logo_url'):
        project_data['logo_url'] = top_logo.get('url')

    team_img = payload.get('team_image') or payload.get('teamImage') or payload.get('team_image_url')
    if isinstance(team_img, dict) and 'team_image_url' in model_fields and not project_data.get('team_image_url'):
        project_data['team_image_url'] = team_img.get('url')

    product_images = payload.get('product_images') or payload.get('productImages')
    if isinstance(product_images, list) and product_images and 'product_image_url' in model_fields and not project_data.get('product_image_url'):
        first = product_images[0]
        if isinstance(first, dict) and first.get('url'):
            project_data['product_image_url'] = first.get('url')

    # top-level tags -> meta.tags
    if 'tags' in payload and 'tags' not in project_data:
        if meta is None:
            meta = {}
        meta['tags'] = payload.get('tags')

    # ensure owner id set by backend
    if meta is None:
        meta = {}
    if isinstance(meta, dict):
        meta['owner_id'] = current_user.id

    if sections:
        project_data['sections'] = sections
    if meta:
        project_data['meta'] = meta

    try:
        project_obj = schemas.ProjectCreate(**project_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid project payload: {e}")

    try:
        return service.create_project(db=db, founder=current_user, project_data=project_obj)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        # Return the exception message and traceback for debugging (Postman)
        raise HTTPException(status_code=500, detail={"error": str(e), "trace": tb})


@router.get("/", response_model=List[schemas.ProjectRead])
def read_projects(
        all_projects: bool = Query(False),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if all_projects:
        # Admin or public list all projects
        return service.get_all_projects(db=db, skip=skip, limit=limit)
    else:
        return service.get_projects_by_founder(db=db, founder_id=current_user.id)


@router.get("/{project_id}", response_model=schemas.ProjectRead)
def read_project_details(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Allow public access for published projects
    from src.database.models import Project
    project_db = db.query(Project).filter(Project.id == project_id).first()
    if not project_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project_db.status == "published":
        # Public access for published projects
        return service.project_to_response(project_db)
    else:
        # Require auth and founder access for drafts
        if not current_user or project_db.founder_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return service.project_to_response(project_db)


@router.patch("/{project_id}", response_model=schemas.ProjectRead)
async def update_project(
        project_id: int,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payload = await request.json()

    # Similar to create, parse the payload
    if hasattr(schemas.ProjectCreate, 'model_fields'):
        model_fields = set(schemas.ProjectCreate.model_fields.keys())
    else:
        model_fields = set(getattr(schemas.ProjectCreate, '__fields__', {}).keys())

    project_data = {}
    sections = {}
    meta = None

    for k, v in payload.items():
        if k == 'meta' or k in ('profile_meta', 'profileMeta'):
            meta = v
            continue
        if k in model_fields:
            project_data[k] = v
        else:
            sections[k] = v

    # Similar extractions as in create
    basic = sections.get('basic') if isinstance(sections.get('basic'), dict) else None
    if basic:
        if not project_data.get('name'):
            project_data['name'] = basic.get('name') or basic.get('projectName')
        if 'tagline' in model_fields and not project_data.get('tagline'):
            project_data['tagline'] = basic.get('tagline') or basic.get('subtitle')
        if 'description' in model_fields and not project_data.get('description'):
            project_data['description'] = basic.get('summary') or basic.get('description')
        logo = basic.get('logo')
        if logo and isinstance(logo, dict) and 'logo_url' in model_fields and not project_data.get('logo_url'):
            project_data['logo_url'] = logo.get('url')

    top_logo = payload.get('logo')
    if top_logo and isinstance(top_logo, dict) and 'logo_url' in model_fields and not project_data.get('logo_url'):
        project_data['logo_url'] = top_logo.get('url')

    team_img = payload.get('team_image') or payload.get('teamImage') or payload.get('team_image_url')
    if isinstance(team_img, dict) and 'team_image_url' in model_fields and not project_data.get('team_image_url'):
        project_data['team_image_url'] = team_img.get('url')

    product_images = payload.get('product_images') or payload.get('productImages')
    if isinstance(product_images, list) and product_images and 'product_image_url' in model_fields and not project_data.get('product_image_url'):
        first = product_images[0]
        if isinstance(first, dict) and first.get('url'):
            project_data['product_image_url'] = first.get('url')

    if 'tags' in payload and 'tags' not in project_data:
        if meta is None:
            meta = {}
        meta['tags'] = payload.get('tags')

    if sections:
        project_data['sections'] = sections
    if meta:
        project_data['meta'] = meta

    try:
        project_obj = schemas.ProjectCreate(**project_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid project payload: {e}")

    try:
        return service.update_project(db=db, project_id=project_id, update_data=project_obj, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        service.delete_project(db=db, project_id=project_id, user=current_user)
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{section_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        section_id: int,
        user: User = Depends(get_current_user_from_token_ws)
):
    await websocket.accept()
    db: Session = next(get_db())
    section = service.get_project_section_by_id(db, section_id=section_id, user=user)
    if not section:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        db.close()
        return

    try:
        while True:
            data = await websocket.receive_json()
            try:
                update_data = schemas.ProjectSectionUpdateWS(**data)
            except Exception:
                await websocket.send_json({"status": "error", "message": "Invalid data format"})
                continue

            service.update_project_section(db, section=section, update_data=update_data)
            await websocket.send_json({"status": "saved", "section_id": section_id})

    except WebSocketDisconnect:
        print(f"Client disconnected from section {section_id}")
    finally:
        db.close()


# --- NEW API ENDPOINTS: members, posts, comments, likes, followers ---
@router.post("/{project_id}/members", response_model=schemas.ProjectMemberRead, status_code=status.HTTP_201_CREATED)
def add_member(
        project_id: int,
        member: schemas.ProjectMemberCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        pm = service.add_project_member(db=db, project_id=project_id, member_data=member, added_by=current_user)
        return pm
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/members", response_model=List[schemas.ProjectMemberRead])
def list_members(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return service.get_project_members(db=db, project_id=project_id)


@router.post("/{project_id}/posts", response_model=schemas.ProjectPostRead, status_code=status.HTTP_201_CREATED)
def create_post(
        project_id: int,
        post: schemas.ProjectPostCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        p = service.create_project_post(db=db, project_id=project_id, author=current_user, post_data=post)
        return p
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/posts", response_model=List[schemas.ProjectPostRead])
def list_posts(
        project_id: int,
        limit: int = Query(50, ge=1, le=200),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return service.get_project_posts(db=db, project_id=project_id, limit=limit)


@router.get("/posts/{post_id}", response_model=schemas.ProjectPostRead)
def get_post(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    post = service.get_post_by_id(db=db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.patch("/posts/{post_id}", response_model=schemas.ProjectPostRead)
def update_post(
        post_id: int,
        post_update: schemas.ProjectPostCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        return service.update_post(db=db, post_id=post_id, update_data=post_update, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        service.delete_post(db=db, post_id=post_id, user=current_user)
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/{post_id}/comments", response_model=schemas.PostCommentRead, status_code=status.HTTP_201_CREATED)
def comment_post(
        post_id: int,
        comment: schemas.PostCommentCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        pc = service.add_comment_to_post(db=db, post_id=post_id, author=current_user, comment_data=comment)
        return pc
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/{post_id}/comments", response_model=List[schemas.PostCommentRead])
def list_post_comments(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Return comments for a post as a nested tree (top-level comments with replies).
    Authentication required to access comments.
    """
    try:
        comments = service.get_comments_for_post(db=db, post_id=post_id)
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/{post_id}/like", response_model=schemas.PostLikeRead)
def like_post(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        pl = service.like_post(db=db, post_id=post_id, user=current_user)
        return pl
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/follow", response_model=schemas.ProjectFollowerRead, status_code=status.HTTP_201_CREATED)
def follow_project(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        pf = service.follow_project(db=db, project_id=project_id, user=current_user)
        return pf
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_project(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        res = service.unfollow_project(db=db, project_id=project_id, user=current_user)
        if res is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow record not found")
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/followers", response_model=List[schemas.ProjectFollowerRead])
def list_followers(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return service.get_project_followers(db=db, project_id=project_id)


@router.post("/{project_id}/publish")
async def publish_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a project to the platform"""
    # get_project_by_id expects (db, project_id, user)
    project = service.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(404, "Project not found")

    # `service.get_project_by_id` returns a dict response; use dict access
    if project.get('founder_id') != current_user.id:
        raise HTTPException(403, "Only project founder can publish")

    # Validate required fields — check dict keys
    required = ["name", "description", "tagline"]
    missing = [field for field in required if not project.get(field)]
    if missing:
        raise HTTPException(400, f"Missing required fields: {', '.join(missing)}")

    # Update project status
    project = await service.publish_project(
        db,
        project_id=project_id,
        user_id=current_user.id
    )

    return project


# @router.get("/published", response_model=List[schemas.ProjectRead])
# def get_published_projects(
#     skip: int = Query(default=0, ge=0),
#     limit: int = Query(default=10, le=50),
#     db: Session = Depends(get_db)
# ):
#     """Get list of published projects"""
#     return service.get_published_projects(db=db, skip=skip, limit=limit)


# @router.get("/users/{user_id}/projects", response_model=List[schemas.ProjectRead])
# def get_user_published_projects(
#     user_id: int,
#     skip: int = Query(default=0, ge=0),
#     limit: int = Query(default=10, le=50),
#     db: Session = Depends(get_db)
# ):
#     """Get list of published projects by a specific user"""
#     return service.get_published_projects_by_user(db=db, user_id=user_id, skip=skip, limit=limit)


# Public router for endpoints that don't require auth
public_router = APIRouter(prefix="/public")

@public_router.get("/projects/published", response_model=List[dict])
def get_published_projects_public(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """Get list of published projects"""
    return service.get_published_projects(db=db, skip=skip, limit=limit)


@public_router.get("/projects/users/{user_id}/projects", response_model=List[dict])
def get_user_published_projects_public(
    user_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """Get list of published projects by a specific user"""
    return service.get_published_projects_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
