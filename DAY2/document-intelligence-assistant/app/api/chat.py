import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent import nodes
from app.agent.graph import agent, prep_agent
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["ask"])

OLLAMA_HINT = "The model service did not respond. Is Ollama running, with llama3.2 and nomic-embed-text pulled?"


def sse(event: str, data: dict) -> str:
    """Format one Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post(
    "/ask",
    summary="Ask a question (streamed answer + citations)",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/event-stream": {}},
                     "description": "Server-Sent Events: many `token` events, then `final` (found, citations, "
                                    "tools_used), then `done`. On failure: `error` then `done`."}},
)
def ask(req: ChatRequest):
    def events():
        try:
            state = prep_agent.invoke({"question": req.question, "doc_ids": req.doc_ids})
            if not state.get("chunks"):  # no-answer fallback
                yield sse("token", {"text": state["answer"]})
                yield sse("final", {"found": False, "citations": [], "tools_used": []})
            else:
                parts = []
                for piece in nodes.stream_answer(state):
                    if piece:
                        parts.append(piece)
                        yield sse("token", {"text": piece})
                text = "".join(parts)
                yield sse("final", {
                    "found": True,
                    "citations": nodes.make_citations(text, state["chunks"]),
                    "tools_used": state.get("tools_used", []),
                })
        except Exception:
            yield sse("error", {"message": OLLAMA_HINT})
        yield sse("done", {})

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/ask/sync", response_model=ChatResponse, summary="Ask a question (single JSON response)")
def ask_sync(req: ChatRequest):
    try:
        out = agent.invoke({"question": req.question, "doc_ids": req.doc_ids})
    except Exception:
        raise HTTPException(503, OLLAMA_HINT)
    return {
        "answer": out["answer"],
        "found": out["found"],
        "citations": out.get("citations", []),
        "tools_used": out.get("tools_used", []),
    }
