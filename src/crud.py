from sqlalchemy.orm import Session
from typing import List, Optional
from src import models, schemas
from src.logger import logging


def create_book(db: Session, book: schemas.BookCreate) -> schemas.Book:
    if get_book(db, book.serial_number):
        logging.warning(f"Book {book.serial_number} already exists")
        raise ValueError(f"Book {book.serial_number} already exists")

    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    logging.info(f"Book {db_book.serial_number} created")

    return db_book


def get_book(db: Session, book_serial_number: str) -> Optional[schemas.Book]:
    """
    Get book by serial number
    """

    return (
        db.query(models.Book)
        .filter(models.Book.serial_number == book_serial_number)
        .first()
    )


def get_books(db: Session) -> List[schemas.Book]:
    return db.query(models.Book).all()


def checkout_book(
    db: Session, book_serial_number: str, checkout_data: schemas.BookCheckout
) -> Optional[schemas.Book]:
    db_book = get_book(db, book_serial_number)

    if not db_book:
        logging.warning(f"Book {book_serial_number} not found")
        return None

    if db_book.is_checked_out:
        logging.warning(f"Book {book_serial_number} is already checked out")
        raise ValueError("Book is already checked out")

    db_book.is_checked_out = True
    db_book.borrower_card_number = checkout_data.borrower_card_number
    db_book.borrow_date = checkout_data.borrow_date
    db.commit()
    db.refresh(db_book)
    logging.info(f"Book {book_serial_number} checked out")

    return db_book


def return_book(db: Session, book_serial_number: str) -> Optional[schemas.Book]:
    db_book = get_book(db, book_serial_number)

    if not db_book:
        logging.warning(f"Book {book_serial_number} not found")
        return None

    if not db_book.is_checked_out:
        logging.warning(f"Book {book_serial_number} is not checked out")
        raise ValueError("Book is not checked out")

    db_book.is_checked_out = False
    db_book.borrower_card_number = None
    db_book.borrow_date = None
    db.commit()
    db.refresh(db_book)
    logging.info(f"Book {book_serial_number} returned")

    return db_book


def delete_book(db: Session, book_serial_number: str) -> Optional[schemas.Book]:
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
