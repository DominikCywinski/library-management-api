import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from main import app
from src.database import Base, get_db
from src.routes import router


app.include_router(router)

# SQLite database URL for testing
SQLITE_DATABASE_URL = "sqlite:///:memory:"

# Create a SQLAlchemy engine
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a new database session with a rollback at the end of the test.
    """

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """
    Create a test client that uses the override_get_db fixture to return a session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


def get_valid_book():
    return {
        "title": "Test Book",
        "author": "Test Author",
        "serial_number": "999991",
    }


def test_health_check(test_client):
    response = test_client.get("/healthcheck/")
    assert response.status_code == 200


def test_is_library_empty(test_client):
    response = test_client.get("/books/")
    assert len(response.json()) == 0


def test_create_valid_book(test_client):
    book = get_valid_book()

    response = test_client.post(
        "/books/",
        json=book,
    )

    assert response.status_code == 200
    assert response.json()["title"] == book["title"]
    assert response.json()["author"] == book["author"]
    assert response.json()["serial_number"] == book["serial_number"]


def test_create_invalid_book(test_client):
    """
    Test with invalid serial number
    """

    book = {
        "title": "Test Invalid Book",
        "author": "Test Author",
        "serial_number": "123",
    }
    response = test_client.post(
        "/books/",
        json=book,
    )
    assert response.status_code == 422


def test_delete_book(test_client):
    book = get_valid_book()
    response = test_client.post(
        "/books/",
        json=book,
    )
    response = test_client.delete("/books/999991")
    assert response.status_code == 200


def test_valid_update_book_status(test_client):
    book = get_valid_book()

    response = test_client.post(
        "/books/",
        json=book,
    )
    response = test_client.patch(
        "/books/999991",
        json={
            "is_checked_out": True,
            "borrower_card_number": "123456",
            "borrow_date": "2023-01-01",
        },
    )
    assert response.status_code == 200


def test_invalid_update_book_status(test_client):
    """
    Test with lack of required fields
    """

    book = get_valid_book()

    response = test_client.post(
        "/books/",
        json=book,
    )
    response = test_client.patch(
        "/books/999991",
        json={
            "is_checked_out": True,
            "borrow_date": "2023-01-01",
        },
    )
    assert response.status_code == 422
