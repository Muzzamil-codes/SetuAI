from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.task_store import init_db
from backend.gateway.routes import task, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes SQLite database tables on server startup."""
    init_db()
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


@app.get("/")
def read_root():
    """Healthcheck endpoint."""
    return {"status": "online", "message": "SETU API Gateway is running!"}