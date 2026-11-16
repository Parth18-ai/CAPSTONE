from app.agent.nodes import make_citations

CHUNKS = [
    {"doc_id": "d1", "filename": "a.pdf", "page": 2, "text": "Oil grade 5W-30"},
    {"doc_id": "d1", "filename": "a.pdf", "page": 5, "text": "Brake fluid DOT 4"},
]


def test_only_cited_chunks_are_returned():
    cites = make_citations("Use DOT 4 [2].", CHUNKS)
    assert [c["page"] for c in cites] == [5]


def test_fallback_to_top_chunk_when_no_marker():
    assert make_citations("No markers here", CHUNKS)[0]["page"] == 2


def test_bad_marker_is_ignored():
    assert make_citations("Wrong [9]", CHUNKS)[0]["page"] == 2
