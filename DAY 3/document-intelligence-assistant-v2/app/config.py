"""All settings in one place. Change values in a .env file (see .env.example)
or edit the defaults below. These are the knobs you tune after running evals."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "pdfs"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
LOG_FILE = BASE_DIR / "logs" / "requests.jsonl"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# --- Tuning knobs (change, re-run evals, compare) ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))      # characters per chunk (needs re-ingest)
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))  # shared characters between chunks (needs re-ingest)
TOP_K = int(os.getenv("TOP_K", "4"))                  # how many chunks to retrieve
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "1.0"))  # drop chunks less similar than this (lower = stricter)

# Example hosted-model prices (USD per 1M tokens), only used for the "if hosted" estimate
PRICE_IN_PER_M = float(os.getenv("PRICE_IN_PER_M", "3.0"))
PRICE_OUT_PER_M = float(os.getenv("PRICE_OUT_PER_M", "15.0"))

NO_ANSWER = "I could not find this in the uploaded documents."

PDF_DIR.mkdir(parents=True, exist_ok=True)
