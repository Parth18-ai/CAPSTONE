import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.ingestion.indexer import ingest_pdf
from app.schemas import DocumentInfo, DocumentList
from app.store import chroma

router = APIRouter(prefix="/documents", tags=["documents"])
PDF_DIR = "data/pdfs"


@router.post("", response_model=DocumentInfo, status_code=201)
def upload(file: UploadFile):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")
    os.makedirs(PDF_DIR, exist_ok=True)
    doc_id = "d_" + uuid.uuid4().hex[:8]
    path = os.path.join(PDF_DIR, f"{doc_id}.pdf")
    with open(path, "wb") as f:
        f.write(file.file.read())
    return ingest_pdf(path, doc_id, file.filename)


@router.get("", response_model=DocumentList)
def list_documents():
    return {"documents": chroma.list_docs()}


@router.delete("/{doc_id}", status_code=204)
def delete(doc_id: str):
    if doc_id not in {d["doc_id"] for d in chroma.list_docs()}:
        raise HTTPException(404, "Unknown doc_id")
    chroma.delete_doc(doc_id)
