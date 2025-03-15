from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date


class BookBase(BaseModel):
    """
    Base model for books.
    - `title`: The title of the book.
    - `author`: The author of the book.
    - `serial_number`: The serial number of the book. It is validated to be a 6-digit integer.
    """

    title: str
    author: str
    serial_number: int = Field(
        ..., ge=100000, le=999999, description="6-digit serial number"
    )


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    """
    Class for updating the status of a book, including borrowing and returning.
    - `is_checked_out`: Indicates whether the book is currently borrowed (True) or available (False).
    - `borrower_card_number`: The 6-digit library card number of the borrower (if the book is checked out).
       It is optional and only required when the book is borrowed.
    - `borrow_date`: The date when the book was borrowed. It is optional and only required when the book is borrowed.
    """

    is_checked_out: bool
    borrower_card_number: Optional[int] = Field(
        None,
        ge=100000,
        le=999999,
        description="6-digit user card number",
    )
    borrow_date: Optional[date] = None

    @model_validator(mode="before")
    def check_borrow_fields(cls, values):
        if values.get("is_checked_out"):
            if not values.get("borrower_card_number") or not values.get("borrow_date"):
                raise ValueError(
                    "Both borrower_card_number and borrow_date are required when checking out a book."
                )
        return values


class Book(BookBase):
    """
    Class representing a book in the system (API response).
    - `id`: The unique identifier of the book in the database.
    - `is_checked_out`: Indicates whether the book is currently borrowed (True) or available (False).
    - `borrower_card_number`: The 6-digit library card number of the borrower. This is optional.
    - `borrow_date`: The date when the book was borrowed. This is optional and only present if the book is checked out.

    The `Config` class ensures compatibility with SQLAlchemy ORM, enabling automatic conversion
    from SQLAlchemy models to Pydantic models.
    """

    id: int
    is_checked_out: bool
    borrower_card_number: Optional[int]
    borrow_date: Optional[date]

    class Config:
        orm_mode = True
