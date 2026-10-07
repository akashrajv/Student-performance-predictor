import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.db import init_db
from backend.api.routes_predict import router as predict_router
from backend.api.routes_models import router as models_router
from backend.api.routes_students import router as students_router
from backend.api.routes_llm import router as llm_router
from backend.api.routes_dashboard import router as dashboard_router
from backend.api.routes_train import router as train_router
from backend.api.routes_resume import router as resume_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB is ready
    init_db()
    print("Student Performance Predictor backend initialized.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Student Performance Predictor using Multi-Model ML and Grounded LLM Explanation",
    lifespan=lifespan
)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all Routers
app.include_router(predict_router)
app.include_router(models_router)
app.include_router(students_router)
app.include_router(llm_router)
app.include_router(dashboard_router)
app.include_router(train_router)
app.include_router(resume_router)

@app.get("/api/health")
async def health_check():
    artifacts_ready = (settings.ARTIFACTS_DIR / "xgboost.pkl").exists()
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "author": settings.AUTHOR,
        "version": settings.VERSION,
        "models_trained": artifacts_ready
    }

# Mount frontend production build if available
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
