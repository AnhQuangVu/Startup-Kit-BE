from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List

from src.database.core import get_db
from src.database.models import User, Project
from src.auth.service import get_current_user, oauth2_scheme
from src.users.service import get_user_by_email
from . import schemas, service

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
def create_new_project(
    project: schemas.ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != 'founder':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ nhà sáng lập mới được phép tạo dự án."
        )
    return service.create_project(db=db, founder=current_user, project_data=project)

@router.get("/", response_model=List[schemas.ProjectRead])
def read_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.get_projects_by_founder(db=db, founder_id=current_user.id)

@router.get("/{project_id}", response_model=schemas.ProjectRead)
def read_project_details(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = service.get_project_by_id(db=db, project_id=project_id, user=current_user)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án.")
    return project


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


@router.put("/{project_id}", response_model=schemas.ProjectRead)
def update_project_info(
    project_id: int,
    update_data: schemas.ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = service.update_project(db=db, founder=current_user, project_id=project_id, update_data=update_data)
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án hoặc bạn không có quyền chỉnh sửa.")
    return project

@router.get("/search", response_model=List[schemas.ProjectRead])
def search_projects(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = service.search_projects(db=db, founder_id=current_user.id, query=query)
    if not results:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án phù hợp.")
    return results

@router.delete("/{project_id}", response_model=schemas.ProjectRead)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = service.soft_delete_project(db=db, founder=current_user, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án hoặc bạn không có quyền xoá.")
    return project
