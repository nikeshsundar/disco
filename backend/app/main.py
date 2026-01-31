from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import auth, candidates, assessments, proctoring, recruiters

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CYGNUSA Elite-Hire HR Evaluation System",
    description="AI-Enabled HR Evaluation System for candidate assessment and hiring decisions",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(assessments.router, prefix="/api")
app.include_router(proctoring.router, prefix="/api")
app.include_router(recruiters.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "CYGNUSA Elite-Hire HR Evaluation System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
