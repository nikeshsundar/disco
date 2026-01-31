import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment for serverless
os.environ.setdefault("VERCEL", "1")

from app.main import app

# Vercel expects 'app' not 'handler'
app = app
