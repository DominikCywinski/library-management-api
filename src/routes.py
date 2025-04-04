from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src import schemas, crud
from src.database import get_db

router = APIRouter()


@router.get("/healthcheck/", tags=["healthcheck"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/books/", response_model=schemas.PaginatedBooks, tags=["books"])
def get_books(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max 1000 items"),
    db: Session = Depends(get_db),
):

    return crud.get_books(db, skip=skip, limit=limit)


@router.post("/books/", response_model=schemas.Book, tags=["books"])
def create_book(
    book: schemas.BookCreate, db: Session = Depends(get_db)
) -> schemas.Book:
    try:
        return crud.create_book(db, book)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/books/{serial_number}", response_model=schemas.Book, tags=["books"])
def read_book(serial_number: str, db: Session = Depends(get_db)) -> schemas.Book:
    db_book = crud.get_book(db, serial_number)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.post(
    "/books/{serial_number}/checkout", response_model=schemas.Book, tags=["books"]
)
def checkout_book(
    serial_number: str,
    checkout_data: schemas.BookCheckout,
    db: Session = Depends(get_db),
) -> schemas.Book:
    try:
        db_book = crud.checkout_book(db, serial_number, checkout_data)
        if db_book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return db_book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/books/{serial_number}/return", response_model=schemas.Book, tags=["books"]
)
def return_book(serial_number: str, db: Session = Depends(get_db)) -> schemas.Book:
    try:
        db_book = crud.return_book(db, serial_number)
        if db_book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return db_book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/books/{serial_number}", response_model=schemas.Book, tags=["books"])
def delete_book(serial_number: str, db: Session = Depends(get_db)) -> schemas.Book:
    db_book = crud.delete_book(db, serial_number)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book
