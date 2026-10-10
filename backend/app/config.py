
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017",
)

MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "documind_ai",
)

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
