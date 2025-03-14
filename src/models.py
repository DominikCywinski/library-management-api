from sqlalchemy import Column, Integer, String, Boolean, Date
from src.database import Base


class Book(Base):
    """
    Represents a book in the library system.
    """

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    serial_number = Column(Integer, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    is_checked_out = Column(Boolean, default=False)
    borrower_card_number = Column(Integer, nullable=True)
    borrow_date = Column(Date, nullable=True)
