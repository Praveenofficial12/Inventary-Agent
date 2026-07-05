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

# Serve Frontend SPA static files from single-service deploy
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# In Docker: __file__ is /app/app/main.py so dist is at /app/frontend/dist
# In local dev: dist is at ../../../frontend/dist relative to this file
_here = os.path.dirname(os.path.abspath(__file__))
_candidates = [
    os.path.join(_here, "..", "frontend", "dist"),                      # Docker layout: /app/frontend/dist
    os.path.join(_here, "..", "..", "..", "frontend", "dist"),           # local dev layout
]
frontend_dist = next((p for p in _candidates if os.path.isdir(p)), None)

if frontend_dist:
    frontend_dist = os.path.realpath(frontend_dist)
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{catchall:path}")
    async def serve_frontend(catchall: str):
        api_prefixes = ("auth/", "products/", "categories/", "suppliers/", "inventory/",
                        "upload/", "chat/", "agents/", "reports/", "health", "docs", "openapi.json")
        if any(catchall.startswith(p) for p in api_prefixes):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API route not found")

        file_path = os.path.join(frontend_dist, catchall)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return {"message": "Welcome to AI Inventory Management API"}
else:
    @app.get("/")
    async def root():
        return {"message": "Welcome to AI Inventory Management API"}


