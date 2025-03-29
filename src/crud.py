from sqlalchemy.orm import Session
from src import models, schemas
from src.logger import logging


def create_book(db: Session, book: schemas.BookCreate):
    if get_book(db, book.serial_number):
        logging.warning(f"Book {book.serial_number} already exists")
        raise ValueError(f"Book {book.serial_number} already exists")

    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    logging.info(f"Book {db_book.serial_number} created")

    return db_book


def get_book(db: Session, book_serial_number: str):
    """
    Get book by serial number
    """

    return (
        db.query(models.Book)
        .filter(models.Book.serial_number == book_serial_number)
        .first()
    )


def get_books(db: Session):
    return db.query(models.Book).all()


def update_book_status(
    db: Session, book_serial_number: str, book_update: schemas.BookUpdate
):
    db_book = get_book(db, book_serial_number)

    if db_book:
        for key, value in book_update.model_dump(exclude_unset=True).items():
            setattr(db_book, key, value)
        db.commit()
        db.refresh(db_book)
        logging.info(f"Book {book_serial_number} updated")
    else:
        logging.warning(f"Book {book_serial_number} not found")

    return db_book


def delete_book(db: Session, book_serial_number: str):
    """
    Delete book by serial number
    """

    db_book = get_book(db, book_serial_number)

    if db_book:
        db.delete(db_book)
        db.commit()
        logging.info(f"Book {book_serial_number} deleted")
    else:
        logging.warning(f"Book {book_serial_number} not found")

    return db_book
