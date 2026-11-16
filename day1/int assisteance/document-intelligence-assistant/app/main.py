from fastapi import FastAPI

from app.api import chat, documents

app = FastAPI(title="Document Intelligence Assistant")
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
