from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Any
from datetime import datetime
from src.database.models import ProjectStage

class ProjectSectionRead(BaseModel):
    id: int
    type: str
    title: str
    content: Optional[dict] = None
    file_url: Optional[HttpUrl] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectSectionUpdateWS(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    tagline: Optional[str] = Field(None, max_length=255)
    stage: ProjectStage = ProjectStage.IDEA
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None

class ProjectRead(BaseModel):
    id: int
    founder_id: int
    name: str
    tagline: Optional[str]
    stage: ProjectStage
    created_at: datetime
    updated_at: datetime
    sections: List[ProjectSectionRead]

    class Config:
        from_attributes = True