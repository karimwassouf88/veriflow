import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# 1. Isolated SQLite Test Engine
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Automatically Redirect File Storage to a Throwaway Temp Directory
@pytest.fixture(autouse=True)
def _use_tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "documents_storage_path", tmp_path)

# 3. Global DB Lifecycle Management
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# 4. Per-Test Isolated DB Session
@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()

# 5. FastApi TestClient with Dependency Override
@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()