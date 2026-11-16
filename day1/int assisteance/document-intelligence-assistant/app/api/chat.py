from fastapi import APIRouter

from app.agent.graph import agent
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    out = agent.invoke({"question": req.question, "doc_ids": req.doc_ids})
    return {
        "answer": out["answer"],
        "found": out["found"],
        "citations": out.get("citations", []),
        "tools_used": out.get("tools_used", []),
    }
