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


def get_valid_checkout_data():
    return {
        "borrower_card_number": "123456",
        "borrow_date": "2023-01-01",
    }


def test_health_check(test_client):
    response = test_client.get("/healthcheck/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_is_library_empty(test_client):
    response = test_client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
    assert data["total"] == 0


def test_create_valid_book(test_client):
    book = get_valid_book()
    response = test_client.post("/books/", json=book)

    assert response.status_code == 200
    assert response.json()["title"] == book["title"]
    assert response.json()["author"] == book["author"]
    assert response.json()["serial_number"] == book["serial_number"]
    assert response.json()["is_checked_out"] is False
    assert response.json()["borrower_card_number"] is None
    assert response.json()["borrow_date"] is None


def test_create_invalid_book(test_client):
    """
    Test with invalid serial number
    """
    book = {
        "title": "Test Invalid Book",
        "author": "Test Author",
        "serial_number": "123",  # Invalid - too short
    }
    response = test_client.post("/books/", json=book)
    assert response.status_code == 422


def test_get_book(test_client):
    book = get_valid_book()
    response = test_client.post("/books/", json=book)
    serial_number = book["serial_number"]

    response = test_client.get(f"/books/{serial_number}")
    assert response.status_code == 200
    assert response.json()["serial_number"] == serial_number


def test_get_nonexistent_book(test_client):
    response = test_client.get("/books/000000")
    assert response.status_code == 404


def test_delete_book(test_client):
    book = get_valid_book()
    response = test_client.post("/books/", json=book)
    serial_number = book["serial_number"]

    response = test_client.delete(f"/books/{serial_number}")
    assert response.status_code == 200
    assert response.json()["serial_number"] == serial_number

    # Verify book is deleted
    response = test_client.get(f"/books/{serial_number}")
    assert response.status_code == 404


def test_checkout_book(test_client):
    # Create book
    book = get_valid_book()
    response = test_client.post("/books/", json=book)
    serial_number = book["serial_number"]

    # Checkout book
    checkout_data = get_valid_checkout_data()
    response = test_client.post(
        f"/books/{serial_number}/checkout",
        json=checkout_data,
    )

    assert response.status_code == 200
    assert response.json()["is_checked_out"] is True
    assert (
        response.json()["borrower_card_number"] == checkout_data["borrower_card_number"]
    )
    assert response.json()["borrow_date"] == checkout_data["borrow_date"]


def test_return_book(test_client):
    # Create and checkout book
    book = get_valid_book()
    response = test_client.post("/books/", json=book)
    serial_number = book["serial_number"]

    checkout_data = get_valid_checkout_data()
    response = test_client.post(
        f"/books/{serial_number}/checkout",
        json=checkout_data,
    )

    # Return book
    response = test_client.post(f"/books/{serial_number}/return")

    assert response.status_code == 200
    assert response.json()["is_checked_out"] is False
    assert response.json()["borrower_card_number"] is None
    assert response.json()["borrow_date"] is None


def test_cannot_checkout_already_checked_out_book(test_client):
    # Create and checkout book
    book = get_valid_book()
    response = test_client.post("/books/", json=book)
    serial_number = book["serial_number"]

    checkout_data = get_valid_checkout_data()
    response = test_client.post(
        f"/books/{serial_number}/checkout",
        json=checkout_data,
    )

    # Try to checkout again
    response = test_client.post(
        f"/books/{serial_number}/checkout",
        json=get_valid_checkout_data(),
    )

    assert response.status_code == 400
    assert "Book is already checked out" in response.json()["detail"]


def test_cannot_return_not_checked_out_book(test_client):
    # Create book
    book = get_valid_book()
    response = test_client.post("/books/", json=book)
    serial_number = book["serial_number"]

    # Try to return
    response = test_client.post(f"/books/{serial_number}/return")

    assert response.status_code == 400
    assert "Book is not checked out" in response.json()["detail"]


def test_checkout_with_invalid_data(test_client):
    # Create book
    book = get_valid_book()
    response = test_client.post("/books/", json=book)
    serial_number = book["serial_number"]

    # Try checkout with missing borrower_card_number
    invalid_data = {"borrow_date": "2023-01-01"}
    response = test_client.post(
        f"/books/{serial_number}/checkout",
        json=invalid_data,
    )

    assert response.status_code == 422

    # Try checkout with invalid card number format
    invalid_data = {
        "borrower_card_number": "123",
        "borrow_date": "2023-01-01",
    }
    response = test_client.post(
        f"/books/{serial_number}/checkout",
        json=invalid_data,
    )

    assert response.status_code == 422


def test_pagination(test_client):
    for i in range(1, 6):
        book = get_valid_book()
        book["serial_number"] = f"99999{i}"
        test_client.post("/books/", json=book)

    response = test_client.get("/books/?skip=2&limit=2")
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["skip"] == 2
    assert data["limit"] == 2
