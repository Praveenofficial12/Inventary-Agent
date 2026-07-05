from fastapi import FastAPI

# Allow running locally without installing package
# (e.g., `uvicorn app.main:app` with PYTHONPATH configured)

from fastapi.middleware.cors import CORSMiddleware

from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.routes import auth, products, categories, suppliers, inventory, upload, chat, agents, reports
from app.db.chroma import connect_to_chroma
from app.config import settings



import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS setup
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and Shutdown events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    connect_to_chroma()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(agents.router)
app.include_router(reports.router)

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to AI Inventory Management API"}
