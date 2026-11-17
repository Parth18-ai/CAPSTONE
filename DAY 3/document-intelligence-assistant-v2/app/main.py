"""FastAPI backend.  Run:  uvicorn app.main:app --reload --port 8000
Routes: GET /health, POST /ingest (PDF upload), POST /ask, GET /metrics"""
from pathlib import Path

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import config, metrics
from .ingest import ingest_pdf
from .rag import answer_question
from .store import get_collection

app = FastAPI(title="Document Intelligence Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

OLLAMA_DOWN = ("Cannot reach Ollama. Start it with 'ollama serve' and make sure the models are "
               f"pulled: ollama pull {config.CHAT_MODEL} && ollama pull {config.EMBED_MODEL}")


class AskIn(BaseModel):
    question: str


@app.get("/health")
def health():
    try:
        requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=3).raise_for_status()
        ollama_ok = True
    except Exception:
        ollama_ok = False
    return {"status": "ok", "ollama": ollama_ok, "chunks_stored": get_collection().count(),
            "chat_model": config.CHAT_MODEL, "embed_model": config.EMBED_MODEL,
            "settings": {"chunk_size": config.CHUNK_SIZE, "overlap": config.CHUNK_OVERLAP,
                         "top_k": config.TOP_K}}


@app.post("/ingest")
def ingest(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    dest = config.PDF_DIR / Path(file.filename).name
    dest.write_bytes(file.file.read())
    try:
        return ingest_pdf(dest)
    except requests.exceptions.ConnectionError:
        raise HTTPException(503, OLLAMA_DOWN)
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.post("/ask")
def ask(body: AskIn):
    try:
        return answer_question(body.question)
    except requests.exceptions.ConnectionError:
        raise HTTPException(503, OLLAMA_DOWN)


@app.get("/metrics")
def get_metrics():
    return metrics.summary()
