"""Everything that touches ChromaDB. Vectors are made by Ollama and handed to Chroma."""
import chromadb

from app.config import settings
from app.llm.provider import get_llm

_client = chromadb.PersistentClient(path=settings.chroma_dir)
_col = _client.get_or_create_collection("manuals", metadata={"hnsw:space": "cosine"})
_llm = get_llm()


def add_chunks(doc_id: str, filename: str, items: list[tuple[int, str]]) -> None:
    if not items:
        return
    texts = [text for _, text in items]
    _col.add(
        ids=[f"{doc_id}-{i}" for i in range(len(items))],
        documents=texts,
        embeddings=_llm.embed(texts),
        metadatas=[{"doc_id": doc_id, "filename": filename, "page": page} for page, _ in items],
    )


def search(question: str, k: int, doc_ids: list[str] | None = None) -> list[dict]:
    where = {"doc_id": {"$in": doc_ids}} if doc_ids else None
    res = _col.query(
        query_embeddings=_llm.embed([question], is_query=True),
        n_results=k,
        where=where,
    )
    hits = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": text, "distance": dist, **meta})
    return hits


def delete_doc(doc_id: str) -> None:
    _col.delete(where={"doc_id": doc_id})


def list_docs() -> list[dict]:
    metas = _col.get(include=["metadatas"])["metadatas"]
    docs: dict[str, dict] = {}
    for m in metas:
        d = docs.setdefault(m["doc_id"], {"doc_id": m["doc_id"], "filename": m["filename"],
                                          "pages": 0, "chunks": 0})
        d["pages"] = max(d["pages"], m["page"])  # highest page seen (approximation)
        d["chunks"] += 1
    return list(docs.values())
