"""
ResearchIQ Backend Application Entrypoint.
Production-grade FastAPI app with modular routers, database initialization, and CORS.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.database.session import engine, Base
from app.routers import auth, papers, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown routines."""
    logger.info("Initializing ResearchIQ database schemas...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified.")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Switching to local SQLite storage.")
        from app.database import session
        from sqlalchemy import create_engine
        session.engine = create_engine("sqlite:///./researchiq.db", connect_args={"check_same_thread": False})
        session.SessionLocal.configure(bind=session.engine)
        Base.metadata.create_all(bind=session.engine)
        logger.info("Initialized local SQLite database schemas.")
    yield
    logger.info("ResearchIQ backend shutdown complete.")


app = FastAPI(
    title="ResearchIQ API",
    description="AI-Powered Research Paper Analysis, Quality Assessment & Publication Readiness Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(analysis.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Verify backend API operational status and configuration."""
    return {
        "status": "healthy",
        "service": "ResearchIQ API",
        "version": "1.0.0",
        "environment": "production-ready",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip()),
    }


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to ResearchIQ API. Access documentation at /docs",
        "documentation": "/docs"
    }
