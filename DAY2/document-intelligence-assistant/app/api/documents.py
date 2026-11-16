import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.ingestion.indexer import ingest_pdf
from app.schemas import DocumentInfo, DocumentList
from app.store import chroma

router = APIRouter(tags=["documents"])
UPLOAD_DIR = "data/uploads"  # API uploads go here; data/pdfs is for the sample manuals


@router.post("/ingest", response_model=DocumentInfo, status_code=201)
def ingest(file: UploadFile):
    """Upload one PDF: extract text, chunk it, embed it, store it in ChromaDB."""
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")
    if filename in {d["filename"] for d in chroma.list_docs()}:
        raise HTTPException(409, f"'{filename}' is already ingested. Delete it first to re-ingest.")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    doc_id = "d_" + uuid.uuid4().hex[:8]
    path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
    with open(path, "wb") as f:
        f.write(file.file.read())
    try:
        info = ingest_pdf(path, doc_id, filename)
    except Exception:
        _cleanup(doc_id, path)
        raise HTTPException(503, "Could not ingest this PDF. Is the file a valid PDF, and is Ollama "
                                 "running with nomic-embed-text pulled?")
    if info["chunks"] == 0:
        _cleanup(doc_id, path)
        raise HTTPException(422, "No readable text found (is this a scanned PDF?)")
    return info


def _cleanup(doc_id: str, path: str) -> None:
    """Remove half-finished work after a failed ingest."""
    try:
        chroma.delete_doc(doc_id)
    except Exception:
        pass
    if os.path.exists(path):
        os.remove(path)


@router.get("/documents", response_model=DocumentList)
def list_documents():
    return {"documents": chroma.list_docs()}


@router.delete("/documents/{doc_id}", status_code=204)
def delete(doc_id: str):
    if doc_id not in {d["doc_id"] for d in chroma.list_docs()}:
        raise HTTPException(404, "Unknown doc_id")
    chroma.delete_doc(doc_id)
