import sys
import os

# Get the directory where this script is located
backend_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the backend directory is in the path
sys.path.insert(0, backend_dir)

# Change working directory to backend folder
os.chdir(backend_dir)

if __name__ == "__main__":
    import uvicorn
    # Disable reload to prevent constant restarts
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
