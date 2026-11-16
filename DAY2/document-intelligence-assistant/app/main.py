from fastapi import FastAPI

from app.api import chat, documents
from app.llm.provider import get_llm
from app.store import chroma

app = FastAPI(title="Document Intelligence Assistant")
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    """Is the API up, is Ollama reachable, how many documents are stored?"""
    try:
        get_llm().client.list()
        ollama_ok = True
    except Exception:
        ollama_ok = False
    return {"status": "ok" if ollama_ok else "degraded", "ollama": ollama_ok,
            "documents": len(chroma.list_docs())}
