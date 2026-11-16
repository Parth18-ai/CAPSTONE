from app.ingestion.chunker import chunk_text


def test_chunks_overlap():
    text = "a" * 250
    chunks = chunk_text(text, size=100, overlap=20)
    assert len(chunks) == 4 and all(len(c) <= 100 for c in chunks)
