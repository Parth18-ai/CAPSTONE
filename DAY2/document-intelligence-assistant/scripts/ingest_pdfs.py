"""Ingest every PDF in a folder into ChromaDB (skips files that are already ingested).

Usage (from the project folder, with .venv active and Ollama running):
    python -m scripts.ingest_pdfs                 # ingests data/pdfs/*.pdf
    python -m scripts.ingest_pdfs path/to/folder
    python -m scripts.ingest_pdfs --dry-run       # only read + chunk, no Ollama/ChromaDB
"""
import argparse
import glob
import os
import sys
import time
import uuid

from app.config import settings
from app.ingestion.chunker import chunk_text
from app.ingestion.loader import load_pdf


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest PDFs into the vector store")
    ap.add_argument("folder", nargs="?", default="data/pdfs")
    ap.add_argument("--dry-run", action="store_true", help="read and chunk only; nothing is stored")
    args = ap.parse_args()

    pdfs = sorted(glob.glob(os.path.join(args.folder, "*.pdf")))
    if not pdfs:
        print(f"No PDFs found in {args.folder}")
        return 1

    if not args.dry_run:
        from app.ingestion.indexer import ingest_pdf  # imported here so --dry-run needs no Chroma
        from app.store import chroma
        already = {d["filename"] for d in chroma.list_docs()}

    print(f"{'FILE':36} {'PAGES':>5} {'CHUNKS':>6}  STATUS")
    total_pages = total_chunks = ingested = 0
    for path in pdfs:
        name = os.path.basename(path)
        t = time.time()
        if args.dry_run:
            pages = load_pdf(path)
            chunks = sum(len(chunk_text(text, settings.chunk_size, settings.chunk_overlap))
                         for _, text in pages)
            status = "dry-run (not stored)"
            n_pages = len(pages)
        elif name in already:
            print(f"{name:36} {'-':>5} {'-':>6}  skipped (already ingested)")
            continue
        else:
            info = ingest_pdf(path, "d_" + uuid.uuid4().hex[:8], name)
            n_pages, chunks = info["pages"], info["chunks"]
            status = f"ingested ({time.time() - t:.1f}s)"
            ingested += 1
        total_pages += n_pages
        total_chunks += chunks
        print(f"{name:36} {n_pages:>5} {chunks:>6}  {status}")

    print(f"\nDone: {len(pdfs)} PDF(s) found, {ingested} newly ingested, "
          f"{total_pages} pages, {total_chunks} chunks processed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
