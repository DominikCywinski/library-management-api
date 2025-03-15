from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.logger import logging

DATABASE_URL = "postgresql://user:password@db:5432/library"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    logging.info("Database initialized")
