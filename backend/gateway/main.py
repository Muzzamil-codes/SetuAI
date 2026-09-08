import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.db.task_store import init_db
from backend.gateway.routes import task, upload, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes SQLite database tables and output directories on server startup."""
    init_db()
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    yield


app = FastAPI(
    title="SETU Gateway API",
    description="API Gateway for the SETU AI Document Processing System",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(task.router)
app.include_router(upload.router)
app.include_router(settings.router)

# Serve generated artifacts as static files
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/download/{file_path:path}")
def download_file(file_path: str):
    """Explicit download endpoint forcing attachment headers for all browsers."""
    clean_path = file_path.replace("outputs/", "").lstrip("/")
    full_path = os.path.join("outputs", clean_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"File '{file_path}' not found on server")
    
    filename = os.path.basename(full_path)
    return FileResponse(
        full_path,
        media_type="application/octet-stream",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/")
def read_root():
    """Healthcheck endpoint."""
    return {"status": "online", "message": "SETU API Gateway is running!"}