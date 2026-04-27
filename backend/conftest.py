import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, time
from typing import Generator
import jwt
import os

# Set test environment variables BEFORE importing app
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from app.main import app
from app.database import Base, get_db
from app.models import User, Pet, Routine, RoutineTask
from app.auth import get_password_hash
from app.constants import UserRole

# Use in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
SECRET_KEY_TEST = "test-secret-key-for-testing-only"
ALGORITHM = "HS256"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    """Override the database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def setup_db():
    """Create all tables at the start of test session"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(setup_db) -> Generator[Session, None, None]:
    """Provide a clean database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """Create a test client with overridden database"""
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test regular user"""
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("TestPass123!"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db: Session) -> User:
    """Create a test admin user"""
    user = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """Generate JWT token for test user"""
    access_token_expires = timedelta(minutes=30)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": test_user.email, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY_TEST, algorithm=ALGORITHM
    )
    return encoded_jwt


@pytest.fixture
def test_admin_token(test_admin_user: User) -> str:
    """Generate JWT token for test admin user"""
    access_token_expires = timedelta(minutes=30)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": test_admin_user.email, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY_TEST, algorithm=ALGORITHM
    )
    return encoded_jwt


@pytest.fixture
def auth_headers(test_user_token: str) -> dict:
    """Return authorization headers for test user"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def admin_headers(test_admin_token: str) -> dict:
    """Return authorization headers for test admin"""
    return {"Authorization": f"Bearer {test_admin_token}"}


@pytest.fixture
def other_user(db: Session) -> dict:
    """Create a second test user with a JWT token for isolation tests"""
    user = User(
        name="Other User",
        email="other@example.com",
        password_hash=get_password_hash("OtherPass123!"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token_expires = timedelta(minutes=30)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": user.email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY_TEST, algorithm=ALGORITHM)

    return {"id": user.id, "email": user.email, "token": token}


@pytest.fixture
def test_user_with_pet(db: Session, test_user: User) -> Pet:
    """Create a test user with a pet, routine, and task for pagination tests"""
    pet = Pet(
        user_id=test_user.id,
        name="TestPet",
        species="dog",
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)

    routine = Routine(pet_id=pet.id)
    db.add(routine)
    db.commit()
    db.refresh(routine)

    task = RoutineTask(
        routine_id=routine.id,
        type="feeding",
        frequency="daily",
        time=time(9, 0),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return pet
