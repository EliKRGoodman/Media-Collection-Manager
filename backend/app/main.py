from fastapi import FastAPI

from app.db.session import test_database_connection

app = FastAPI(title="Media Collection API")


@app.get("/")
def root():
    return {"message": "Media Collection API is running"}


@app.get("/health/db")
def database_health_check():
    test_database_connection()
    return {"database": "connected"}