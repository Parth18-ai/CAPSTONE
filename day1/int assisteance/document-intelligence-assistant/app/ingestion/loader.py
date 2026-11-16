"""Step 1 of ingestion: PDF -> list of (page_number, text)."""
import fitz  # PyMuPDF


def load_pdf(path: str) -> list[tuple[int, str]]:
    doc = fitz.open(path)
    pages = [(i + 1, page.get_text()) for i, page in enumerate(doc)]
    doc.close()
    return pages
