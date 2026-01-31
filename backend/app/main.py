import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CYGNUSA Elite-Hire HR Evaluation System",
    description="AI-Enabled HR Evaluation System for candidate assessment and hiring decisions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Import routers after app is created
try:
    from app.api import auth, candidates, assessments, proctoring, recruiters
    app.include_router(auth.router, prefix="/api")
    app.include_router(candidates.router, prefix="/api")
    app.include_router(assessments.router, prefix="/api")
    app.include_router(proctoring.router, prefix="/api")
    app.include_router(recruiters.router, prefix="/api")
except Exception as e:
    print(f"Router import error: {e}")
    
    # Add fallback error endpoint
    @app.get("/api/error")
    async def error_info():
        return {"error": str(e)}

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database initialization error: {e}")
