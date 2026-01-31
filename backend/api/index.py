import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment for serverless
os.environ.setdefault("VERCEL", "1")

try:
    from app.main import app
except Exception as e:
    # Fallback minimal app if main app fails
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"error": str(e), "message": "Main app failed to load"}
    
    @app.get("/api/health")
    def health():
        return {"status": "error", "detail": str(e)}
