"""The 'memory' that flows through the graph. Each node reads it and returns updates."""
from typing import TypedDict


class AgentState(TypedDict, total=False):
    question: str
    doc_ids: list[str] | None
    chunks: list[dict]
    tools_used: list[dict]
    tool_note: str
    answer: str
    found: bool
    citations: list[dict]
