from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Any, Dict
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

class StageItem(BaseModel):
    id: str
    title: str
    description_html: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    deliverables: Optional[List[str]] = None
    budget: Optional[float] = None
    progress_percent: Optional[int] = None
    dependencies: Optional[List[str]] = None

class MediaRef(BaseModel):
    url: Optional[HttpUrl] = None
    public_id: Optional[str] = None

class ProjectCreate(BaseModel):
    # Core project fields that will remain on the Project row
    name: str = Field(..., min_length=3, max_length=255)
    tagline: Optional[str] = Field(None, max_length=500)
    stage: Optional[ProjectStage] = None
    description: Optional[str] = None

    # media
    logo: Optional[MediaRef] = None
    logo_url: Optional[HttpUrl] = None
    team_image: Optional[MediaRef] = None
    product_images: Optional[List[MediaRef]] = None

    # basic website
    website_url: Optional[HttpUrl] = None
    profile_url: Optional[HttpUrl] = None
    use_ai: Optional[bool] = False

    # business/product fields
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
    cost_estimate: Optional[Any] = None
    capital_source: Optional[str] = None
    revenue_goal: Optional[Any] = None
    member_count: Optional[int] = None
    member_skills: Optional[str] = None
    resources: Optional[str] = None
    deployment_location: Optional[str] = None

    # stages and progress
    stages: Optional[List[StageItem]] = None
    current_stage: Optional[str] = None
    current_stage_label: Optional[str] = None

    # meta and flexible sections
    meta: Optional[Any] = None
    sections: Optional[Any] = None

    class Config:
        from_attributes = True

class ProjectRead(BaseModel):
    # Core project fields
    id: int
    founder_id: int
    name: str
    tagline: Optional[str]
    stage: Optional[ProjectStage]
    description: Optional[str]

    # media and links
    logo: Optional[MediaRef]
    logo_url: Optional[HttpUrl]
    team_image: Optional[MediaRef]
    product_images: Optional[List[MediaRef]]

    website_url: Optional[HttpUrl]
    profile_url: Optional[HttpUrl]
    use_ai: Optional[bool]

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
    cost_estimate: Optional[Any]
    capital_source: Optional[str]
    revenue_goal: Optional[Any]
    member_count: Optional[int]
    member_skills: Optional[str]
    resources: Optional[str]
    deployment_location: Optional[str]

    stages: Optional[List[StageItem]]
    current_stage: Optional[str]
    current_stage_label: Optional[str]

    meta: Optional[Any]

    # sections: returned as key->value mapping to match the FE payload
    sections: Optional[Dict[str, Any]] = None

    stages: Optional[List[StageItem]] = None
    current_stage: Optional[str] = None
    current_stage_label: Optional[str] = None

    meta: Optional[Any] = None

    # sections: FE/tests sometimes pass a list of sections; accept flexible type
    sections: Optional[Any] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # tests expect this flag
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class ProjectPublishedRead(BaseModel):
    id: int
    name: str
    tagline: Optional[str]
    description: Optional[str]
    logo_url: Optional[HttpUrl]
    website_url: Optional[HttpUrl]
    industry: Optional[str]
    created_at: datetime
    published_at: Optional[datetime]
    founder_id: int

    class Config:
        from_attributes = True


# --- NEW SCHEMAS: members, posts, media, likes, comments, followers ---
class ProjectMemberRead(BaseModel):
    id: int
    project_id: int
    user_id: Optional[int] = None
    name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    role_in_project: Optional[str] = None
    is_founder: Optional[bool] = False
    joined_at: datetime

    class Config:
        from_attributes = True

class ProjectMemberCreate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    role_in_project: Optional[str] = None
    is_founder: Optional[bool] = False

    class Config:
        from_attributes = True

class MediaItem(BaseModel):
    url: HttpUrl
    public_id: Optional[str] = None
    media_type: Optional[str] = None

    class Config:
        from_attributes = True

class ProjectPostCreate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    media: Optional[List[MediaItem]] = None
    visibility: Optional[str] = "public"

    class Config:
        from_attributes = True

# --- NEW: Author schema so we can return author details with a post ---
class AuthorRead(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True

class ProjectPostRead(BaseModel):
    id: int
    project_id: int
    author_id: Optional[int] = None
    # include nested author object (optional) so frontend can show the name/avatar
    author: Optional[AuthorRead] = None
    title: Optional[str] = None
    body: Optional[str] = None
    visibility: Optional[str] = None
    media: Optional[List[MediaItem]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostLikeRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PostCommentCreate(BaseModel):
    body: str
    parent_comment_id: Optional[int] = None

    class Config:
        from_attributes = True

class PostCommentRead(BaseModel):
    id: int
    post_id: int
    author_id: int
    # include nested author info so FE can display name/avatar
    author: Optional[AuthorRead] = None
    body: str
    parent_comment_id: Optional[int] = None
    created_at: datetime
    # nested replies (list of comment dicts). Use flexible typing to avoid forward refs.
    replies: Optional[List[Any]] = None

    class Config:
        from_attributes = True

class ProjectFollowerRead(BaseModel):
    id: int
    project_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectFollowCreate(BaseModel):
    # empty body accepted; we only need current user in backend
    pass
