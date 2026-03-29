import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "backend/resume_app.db")
FILE_DB_ROOT: str = os.getenv("FILE_DB_ROOT", "file_db")
VLLM_BASE_URL: str = os.getenv("VLLM_BASE_URL", "http://localhost:8000")
VLLM_MODEL_NAME: str = os.getenv("VLLM_MODEL_NAME", "default")

# Resolve paths relative to the project root (parent of this file's directory)
_PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = _PROJECT_ROOT / DATABASE_URL
FILE_DB_PATH = _PROJECT_ROOT / FILE_DB_ROOT
