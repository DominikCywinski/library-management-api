from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src import schemas, crud
from src.database import get_db, init_db


app = FastAPI(on_startup=[init_db])


# Add health check
@app.get("/healthcheck/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/books/", response_model=list[schemas.Book])
def get_books(db: Session = Depends(get_db)) -> list[schemas.Book]:
    return crud.get_books(db)


@app.post("/books/", response_model=schemas.Book)
def create_book(
    book: schemas.BookCreate, db: Session = Depends(get_db)
) -> schemas.Book:
    try:
        return crud.create_book(db, book)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/books/{book_serial_number}", response_model=schemas.Book)
def delete_book(book_serial_number: str, db: Session = Depends(get_db)) -> schemas.Book:
    book = crud.delete_book(db, book_serial_number)
    if book is None:
        raise HTTPException(
            status_code=404, detail=f"Book {book_serial_number} not found"
        )

    return book


@app.patch("/books/{book_serial_number}", response_model=schemas.Book)
def update_book_status(
    book_serial_number: str,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
) -> schemas.Book:
    book = crud.update_book_status(db, book_serial_number, book_update)
    if book is None:
        raise HTTPException(
            status_code=404, detail=f"Book {book_serial_number} not found"
        )

    return book
