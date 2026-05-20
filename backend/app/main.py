from fastapi import FastAPI

from app.api.collection_items import router as collection_items_router
from app.db.session import test_database_connection
from app.api.metadata import router as metadata_router

app = FastAPI(title="Media Collection API")

app.include_router(collection_items_router)
app.include_router(metadata_router)


@app.get("/")
def root():
    return {"message": "Media Collection API is running"}


@app.get("/health/db")
def database_health_check():
    test_database_connection()
    return {"database": "connected"}