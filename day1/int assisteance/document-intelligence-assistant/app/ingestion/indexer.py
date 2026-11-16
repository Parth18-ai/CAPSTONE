"""Step 3: PDF -> pages -> chunks -> ChromaDB (each chunk remembers its page)."""
from app.config import settings
from app.ingestion.chunker import chunk_text
from app.ingestion.loader import load_pdf
from app.store import chroma


def ingest_pdf(path: str, doc_id: str, filename: str) -> dict:
    pages = load_pdf(path)
    items = []  # (page, chunk_text)
    for page_no, text in pages:
        for piece in chunk_text(text, settings.chunk_size, settings.chunk_overlap):
            items.append((page_no, piece))
    chroma.add_chunks(doc_id, filename, items)
    return {"doc_id": doc_id, "filename": filename, "pages": len(pages), "chunks": len(items)}
