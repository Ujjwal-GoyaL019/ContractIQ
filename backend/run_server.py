import sys
import os
import uvicorn

# Ensure backend directory is first in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Ensure working directory is backend_dir
os.chdir(backend_dir)

if __name__ == "__main__":
    print(f"Starting ContractIQ FastAPI Server on http://127.0.0.1:8000 (dir: {backend_dir})...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
