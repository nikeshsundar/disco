import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CYGNUSA Elite-Hire HR Evaluation System",
    description="AI-Enabled HR Evaluation System for candidate assessment and hiring decisions",
    version="1.0.0"
)

# CORS configuration - allow Vercel frontend
allowed_origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "https://*.vercel.app",
]

# Add custom frontend URL if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api import auth, candidates, assessments, proctoring, recruiters

app.include_router(auth.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(assessments.router, prefix="/api")
app.include_router(proctoring.router, prefix="/api")
app.include_router(recruiters.router, prefix="/api")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database initialization error: {e}")

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
