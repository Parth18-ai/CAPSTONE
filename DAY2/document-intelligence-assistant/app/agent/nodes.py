"""The steps (nodes) of the agent. Each takes the state and returns what changed."""
import json
import re

from app.agent import tools
from app.agent.state import AgentState
from app.config import settings
from app.llm.provider import get_llm
from app.store import chroma

llm = get_llm()
NOT_FOUND = "I couldn't find this in the uploaded documents."


def retrieve(state: AgentState) -> dict:
    hits = chroma.search(state["question"], settings.top_k, state.get("doc_ids"))
    hits = [h for h in hits if h["distance"] <= settings.max_distance]  # drop weak matches
    return {"chunks": hits}


def decide_tool(state: AgentState) -> dict:
    """Ask the LLM: does this question need a unit conversion? If so, run the tool."""
    context = "\n".join(h["text"] for h in state["chunks"])
    prompt = (
        "Decide if answering needs a unit conversion (units: nm, lbf-ft, psi, bar, l, gal, km, mi).\n"
        'If yes reply JSON: {"use_tool": true, "value": <number from the context>, '
        '"from_unit": "...", "to_unit": "..."}\n'
        'If no reply JSON: {"use_tool": false}\n\n'
        f"Question: {state['question']}\n\nContext:\n{context}"
    )
    try:
        plan = json.loads(llm.chat([{"role": "user", "content": prompt}], json_mode=True))
        if plan.get("use_tool"):
            value = float(plan["value"])
            result = tools.unit_convert(value, plan["from_unit"], plan["to_unit"])
            text_in = f"{value} {plan['from_unit']} -> {plan['to_unit']}"
            return {
                "tools_used": [{"name": "unit_convert", "input": text_in, "output": str(result)}],
                "tool_note": f"Tool result: {text_in} = {result}",
            }
    except Exception:
        pass  # if the tool step fails, just answer without it
    return {"tools_used": [], "tool_note": ""}


SYSTEM_PROMPT = (
    "You answer questions using ONLY the numbered context. "
    "Cite sources like [1] after the facts you use. "
    "If the context does not contain the answer, say you could not find it. Be concise."
)


def build_messages(state: AgentState) -> list[dict]:
    """Put the retrieved chunks (numbered) and the question into a prompt."""
    chunks = state["chunks"]
    context = "\n\n".join(
        f"[{i}] ({c['filename']}, page {c['page']}) {c['text']}" for i, c in enumerate(chunks, 1)
    )
    user = f"Context:\n{context}\n\n{state.get('tool_note', '')}\n\nQuestion: {state['question']}"
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def make_citations(text: str, chunks: list[dict]) -> list[dict]:
    """Citations come from stored metadata, never invented by the model."""
    used = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text)})
    picked = [chunks[n - 1] for n in used if 1 <= n <= len(chunks)] or chunks[:1]
    return [
        {"doc_id": c["doc_id"], "filename": c["filename"], "page": c["page"], "snippet": c["text"][:200]}
        for c in picked
    ]


def answer(state: AgentState) -> dict:
    """Normal (non-streaming) answer node, used by the full graph and the evals."""
    text = llm.chat(build_messages(state))
    return {"answer": text, "found": True, "citations": make_citations(text, state["chunks"])}


def stream_answer(state: AgentState):
    """Streaming version: yields pieces of the answer as the model writes them."""
    yield from llm.chat_stream(build_messages(state))


def not_found(state: AgentState) -> dict:
    return {"answer": NOT_FOUND, "found": False, "citations": [], "tools_used": []}
