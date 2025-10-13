from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from . import schemas
from src.database.models import User, Project, ProjectSection

def create_project(db: Session, founder: User, project_data: schemas.ProjectCreate) -> Project:
    db_project = Project(
        name=project_data.name,
        tagline=project_data.tagline,
        stage=project_data.stage,
        founder_id=founder.id,
        description=project_data.description,
        logo_url=project_data.logo_url,
        website_url=project_data.website_url
    )
    db.add(db_project)
    db.flush() # lấy project.id cho các section

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
            content={}
        )
        db.add(section)

    db.commit()
    db.refresh(db_project)
    return db_project

def get_project_by_id(db: Session, project_id: int, user: User) -> Optional[Project]:
    return db.query(Project)\
        .options(selectinload(Project.sections))\
        .filter(Project.id == project_id, Project.founder_id == user.id)\
        .first()

def get_projects_by_founder(db: Session, founder_id: int) -> List[Project]:
    return db.query(Project)\
        .options(selectinload(Project.sections))\
        .filter(Project.founder_id == founder_id)\
        .order_by(Project.created_at.desc())\
        .all()

def get_project_section_by_id(db: Session, section_id: int, user: User) -> Optional[ProjectSection]:
    return db.query(ProjectSection).join(Project).filter(
        ProjectSection.id == section_id,
        Project.founder_id == user.id
    ).first()

def update_project_section(db: Session, section: ProjectSection, update_data: schemas.ProjectSectionUpdateWS) -> ProjectSection:
    if update_data.title is not None:
        section.title = update_data.title
    if update_data.content is not None:
        section.content = update_data.content
    
    db.add(section)
    db.commit()
    db.refresh(section)
    return section