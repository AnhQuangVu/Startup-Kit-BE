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
    projects = relationship("Project", back_populates="founder")
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
    founder_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    tagline = Column(String(500))
    description = Column(Text)
    logo_url = Column(String(512))
    stage = Column(Enum(ProjectStage), index=True)
    website_url = Column(String(512))
    industry = Column(String(255))
    pain_point = Column(Text)
    solution = Column(Text)
    product = Column(Text)
    customer_segment = Column(String(255))
    customer_features = Column(Text)
    market_size = Column(String(255))
    market_area = Column(String(255))
    business_model = Column(Text)
    revenue_method = Column(String(255))
    distribution_channel = Column(String(255))
    partners = Column(Text)
    cost_estimate = Column(String(255))
    capital_source = Column(String(255))
    revenue_goal = Column(String(255))
    member_count = Column(Integer)
    member_skills = Column(Text)
    resources = Column(Text)
    team_image_url = Column(String(512))
    product_image_url = Column(String(512))
    pdf_url = Column(String(512), nullable=True)
    use_ai = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)  # Trường xoá mềm
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    deployment_location = Column(String(255))

    founder = relationship("User", back_populates="projects")
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