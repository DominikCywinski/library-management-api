from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import date


class BookBase(BaseModel):
    """
    Base model for books.
    - `title`: The title of the book.
    - `author`: The author of the book.
    - `serial_number`: The serial number of the book. It is validated to be a 6-digit integer.
    """

    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    serial_number: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit serial number",
    )


class BookCreate(BookBase):
    pass


class BookCheckout(BaseModel):
    """
    Class for checking out a book.
    - `borrower_card_number`: The 6-digit library card number of the borrower.
    - `borrow_date`: The date when the book was borrowed.
    """

    borrower_card_number: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit user card number",
    )
    borrow_date: date


class Book(BookBase):
    """
    Class representing a book in the system.
    - `id`: The unique identifier of the book in the database.
    - `is_checked_out`: Indicates whether the book is currently borrowed (True) or available (False).
    - `borrower_card_number`: The 6-digit library card number of the borrower. This is optional.
    - `borrow_date`: The date when the book was borrowed. This is optional and only present if the book is checked out.
    """

    id: int
    is_checked_out: bool
    borrower_card_number: Optional[str] = None
    borrow_date: Optional[date] = None

    class Config:
        orm_mode = True


class PaginatedBooks(BaseModel):
    items: List[Book]
    total: int
    skip: int
    limit: int
