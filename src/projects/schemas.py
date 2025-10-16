from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from src.database.models import ProjectStage

class ProjectSectionRead(BaseModel):
    id: int
    type: str
    title: str
    content: Optional[dict] = None
    file_url: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectSectionUpdateWS(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    tagline: Optional[str] = Field(None, max_length=255)
    stage: ProjectStage = ProjectStage.Y_TUONG
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    pain_point: Optional[str] = None
    solution: Optional[str] = None
    product: Optional[str] = None
    customer_segment: Optional[str] = None
    customer_features: Optional[str] = None
    market_size: Optional[str] = None
    market_area: Optional[str] = None
    business_model: Optional[str] = None
    revenue_method: Optional[str] = None
    distribution_channel: Optional[str] = None
    partners: Optional[str] = None
    cost_estimate: Optional[str] = None
    capital_source: Optional[str] = None
    revenue_goal: Optional[str] = None
    member_count: Optional[int] = None
    member_skills: Optional[str] = None
    resources: Optional[str] = None
    team_image_url: Optional[str] = None
    product_image_url: Optional[str] = None
    use_ai: Optional[bool] = None
    is_deleted: Optional[bool] = False  # Trường xoá mềm
    deployment_location: Optional[str] = None

class ProjectRead(BaseModel):
    id: int
    founder_id: int
    name: str
    tagline: Optional[str]
    stage: ProjectStage
    description: Optional[str]
    logo_url: Optional[str]
    website_url: Optional[str]
    # --- Các trường mới ---
    industry: Optional[str]
    pain_point: Optional[str]
    solution: Optional[str]
    product: Optional[str]
    customer_segment: Optional[str]
    customer_features: Optional[str]
    market_size: Optional[str]
    market_area: Optional[str]
    business_model: Optional[str]
    revenue_method: Optional[str]
    distribution_channel: Optional[str]
    partners: Optional[str]
    cost_estimate: Optional[str]
    capital_source: Optional[str]
    revenue_goal: Optional[str]
    member_count: Optional[int]
    member_skills: Optional[str]
    resources: Optional[str]
    team_image_url: Optional[str]
    product_image_url: Optional[str]
    use_ai: Optional[bool]
    created_at: datetime
    updated_at: datetime
    sections: List[ProjectSectionRead]
    is_deleted: Optional[bool] = False  # Trường xoá mềm
    deployment_location: Optional[str]

    class Config:
        from_attributes = True

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    stage: Optional[ProjectStage] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    pain_point: Optional[str] = None
    solution: Optional[str] = None
    product: Optional[str] = None
    customer_segment: Optional[str] = None
    customer_features: Optional[str] = None
    market_size: Optional[str] = None
    market_area: Optional[str] = None
    business_model: Optional[str] = None
    revenue_method: Optional[str] = None
    distribution_channel: Optional[str] = None
    partners: Optional[str] = None
    cost_estimate: Optional[str] = None
    capital_source: Optional[str] = None
    revenue_goal: Optional[str] = None
    member_count: Optional[int] = None
    member_skills: Optional[str] = None
    resources: Optional[str] = None
    team_image_url: Optional[str] = None
    product_image_url: Optional[str] = None
    use_ai: Optional[bool] = None
    is_deleted: Optional[bool] = None
    deployment_location: Optional[str] = None
