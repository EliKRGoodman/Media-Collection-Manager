from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.collection_items import router as collection_items_router
from app.db.session import test_database_connection
from app.api.metadata import router as metadata_router
from app.api.locations import router as locations_router

app = FastAPI(title="Media Collection API")

# Allow frontend development server to access backend API.
#
# V1 development setup:
# - frontend runs on localhost:5173
# - backend runs on localhost:8000
#
# Without CORS configuration, browsers block requests
# between different origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collection_items_router)
app.include_router(metadata_router)
app.include_router(locations_router)

@app.get("/")
def root():
    return {"message": "Media Collection API is running"}


@app.get("/health/db")
def database_health_check():
    test_database_connection()
    return {"database": "connected"}