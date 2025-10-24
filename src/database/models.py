import enum
from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, JSON, Boolean, Text,
    ForeignKey, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .core import Base

class UserRole(str, enum.Enum):
    FOUNDER = "founder"
    INVESTOR = "investor"
    MENTOR = "mentor"
    ADMIN = "admin"

class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class ProjectStage(str, enum.Enum):
    Y_TUONG = "y-tuong"
    NGHIEN_CUU_THI_TRUONG = "nghien-cuu-thi-truong"
    HOAN_THIEN_SAN_PHAM = "hoan-thien-san-pham"
    KHAO_SAT = "khao-sat"
    LAUNCH = "launch"

class NotificationType(str, enum.Enum):
    NEW_CONNECTION_REQUEST = "new_connection_request"
    CONNECTION_ACCEPTED = "connection_accepted"
    PROJECT_UPDATE = "project_update"
    NEW_MESSAGE = "new_message"


project_categories_table = Table('project_categories', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

conversation_participants_table = Table('conversation_participants', Base.metadata,
    Column('conversation_id', Integer, ForeignKey('conversations.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


# --- MODULE: QUẢN LÝ NGƯỜI DÙNG ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    projects = relationship(
        "Project",
        back_populates="founder",
        foreign_keys="[Project.founder_id]"
    )
    published_projects = relationship(
        "Project",
        foreign_keys="[Project.published_by]",
        backref="publisher"
    )
    connections = relationship("Connection", back_populates="investor")
    messages = relationship("Message", back_populates="sender")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
    conversations = relationship("Conversation", secondary=conversation_participants_table, back_populates="participants")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"

    @property
    def avatar_url(self):
        """Proxy property so serializers can read avatar_url from the related profile.
        Returns None if no profile or avatar set.
        """
        if self.profile:
            return self.profile.avatar_url
        return None


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    website_url = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id})>"


# --- MODULE: QUẢN LÝ DỰ ÁN ---
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(50), nullable=False, index=True)

    def __repr__(self):
        return f"<Category(name='{self.name}', type='{self.type}')>"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    founder_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    tagline = Column(String(500))
    description = Column(Text)
    logo_url = Column(String(512))
    stage = Column(Enum(ProjectStage), index=True)
    website_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Flexible columns to store richer payloads
    logo = Column(JSON, nullable=True)  # {url, public_id}
    team_image = Column(JSON, nullable=True)
    product_images = Column(JSON, nullable=True)  # list

    industry = Column(String(255), nullable=True)
    pain_point = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)
    product = Column(Text, nullable=True)
    customer_segment = Column(Text, nullable=True)
    customer_features = Column(Text, nullable=True)
    market_size = Column(String(255), nullable=True)
    market_area = Column(String(255), nullable=True)
    business_model = Column(Text, nullable=True)
    revenue_method = Column(Text, nullable=True)
    distribution_channel = Column(Text, nullable=True)
    partners = Column(Text, nullable=True)
    cost_estimate = Column(String(255), nullable=True)
    capital_source = Column(String(255), nullable=True)
    revenue_goal = Column(String(255), nullable=True)
    member_count = Column(Integer, nullable=True)
    member_skills = Column(String(255), nullable=True)
    resources = Column(Text, nullable=True)
    deployment_location = Column(String(255), nullable=True)
    profile_url = Column(String(512), nullable=True)
    use_ai = Column(Boolean, default=False)

    stages = Column(JSON, nullable=True)
    current_stage = Column(String(100), nullable=True)
    current_stage_label = Column(String(255), nullable=True)

    # Publishing fields
    status = Column(String(50), default="draft")  # draft, published, archived
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_by = Column(Integer, ForeignKey("users.id", ondelete='SET NULL'), nullable=True)

    meta = Column(JSON, nullable=True)

    founder = relationship(
        "User",
        back_populates="projects",
        foreign_keys=[founder_id]
    )
    sections = relationship("ProjectSection", back_populates="project", cascade="all, delete-orphan")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=project_categories_table, backref="projects")
    connections_requests = relationship("Connection", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class ProjectSection(Base):
    __tablename__ = "project_sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(JSON)
    file_url = Column(String(512))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    project = relationship("Project", back_populates="sections")


class ProjectVersion(Base):
    __tablename__ = "project_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(JSON, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="versions")


# --- MODULE: KẾT NỐI VÀ TƯƠNG TÁC ---
class Connection(Base):
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING, nullable=False, index=True)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    investor = relationship("User", back_populates="connections")
    project = relationship("Project", back_populates="connections_requests")
    conversation = relationship("Conversation", back_populates="connection", uselist=False, cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_id = Column(Integer, ForeignKey('connections.id'), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    connection = relationship("Connection", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    participants = relationship("User", secondary=conversation_participants_table, back_populates="conversations")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    
    
# --- MODULE: HỆ THỐNG VÀ HỖ TRỢ ---
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    related_entity_id = Column(Integer)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    recipient = relationship("User", back_populates="notifications")


# --- MODULE: PROJECT MEMBERS / POSTS / MEDIA / FOLLOWERS ---
class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    role_in_project = Column(String(100), nullable=True)
    is_founder = Column(Boolean, default=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", backref="members")
    user = relationship("User", backref="project_members")

    def __repr__(self):
        return f"<ProjectMember(id={self.id}, project_id={self.project_id})>"


class ProjectPost(Base):
    __tablename__ = "project_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    visibility = Column(String(50), default="public", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    project = relationship("Project", backref="posts")
    author = relationship("User", backref="posts")
    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProjectPost(id={self.id}, project_id={self.project_id})>"


class PostMedia(Base):
    __tablename__ = "post_media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('project_posts.id'), nullable=False, index=True)
    url = Column(String(1024), nullable=False)
    public_id = Column(String(255), nullable=True)
    media_type = Column(String(50), nullable=True)
    order = Column(Integer, nullable=True)

    post = relationship("ProjectPost", back_populates="media")

    def __repr__(self):
        return f"<PostMedia(id={self.id}, post_id={self.post_id})>"


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('project_posts.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("ProjectPost", back_populates="likes")
    user = relationship("User", backref="post_likes")

    def __repr__(self):
        return f"<PostLike(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('project_posts.id'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    body = Column(Text, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('post_comments.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("ProjectPost", back_populates="comments")
    author = relationship("User", backref="post_comments")
    parent = relationship("PostComment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<PostComment(id={self.id}, post_id={self.post_id})>"


class ProjectFollower(Base):
    __tablename__ = "project_followers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", backref="followers")
    user = relationship("User", backref="followed_projects")

    def __repr__(self):
        return f"<ProjectFollower(id={self.id}, project_id={self.project_id}, user_id={self.user_id})>"


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True, index=True)
    url = Column(String(1024), nullable=False)
    public_id = Column(String(255), nullable=True)
    type = Column(String(50), nullable=True)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", backref="media_items")
    uploader = relationship("User", backref="uploaded_media")

    def __repr__(self):
        return f"<Media(id={self.id}, url='{self.url}')>"


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True, index=True)
    actor_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", backref="activities")
    actor = relationship("User", backref="activities")

# --- MODULE: AI & RAG DOCUMENTS ---
class Document(Base):
    """Model cho tài liệu được upload để sử dụng trong RAG"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, docx, etc.
    file_size = Column(Integer, nullable=False)  # size in bytes
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True, index=True)
    content_preview = Column(Text, nullable=True)  # Preview của nội dung
    is_processed = Column(Boolean, default=False)  # Đã xử lý và thêm vào vector store chưa
    doc_metadata = Column(JSON, nullable=True)  # Metadata bổ sung
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    uploader = relationship("User", backref="documents")
    project = relationship("Project", backref="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', uploaded_by={self.uploaded_by})>"

