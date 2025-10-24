"""
Test configuration và fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.database.core import Base, get_db
from src.database.models import User, Project, Document, UserRole
from src.core.security import get_password_hash
from src.auth.service import create_access_token

# Tạo in-memory SQLite database cho testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Tạo database mới cho mỗi test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Tạo test client với database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Tạo user cho testing"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        role=UserRole.FOUNDER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_token(test_user):
    """Tạo access token cho user"""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def auth_headers(test_token):
    """Tạo headers với authorization token"""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def test_project(db, test_user):
    """Tạo project mẫu cho testing"""
    project = Project(
        founder_id=test_user.id,
        name="Test Project",
        tagline="A test startup project",
        description="This is a test project for AI features",
        industry="Technology",
        pain_point="Testing pain points",
        solution="Testing solutions",
        product="Test product",
        customer_segment="Test customers",
        market_size="1000",
        business_model="B2B",
        revenue_method="Subscription",
        use_ai=True
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def test_document(db, test_user, test_project):
    """Tạo document mẫu cho testing"""
    document = Document(
        filename="test_doc.pdf",
        file_path="/tmp/test_doc.pdf",
        file_type="pdf",
        file_size=1024,
        uploaded_by=test_user.id,
        project_id=test_project.id,
        is_processed=True,
        content_preview="This is a test document"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
