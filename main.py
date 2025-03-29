from fastapi import FastAPI
from src.database import init_db
from src.routes import router as api_router

app = FastAPI(on_startup=[init_db])

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Welcome to Library API"}
