"""Pydantic models = the API contract. FastAPI uses them to validate and document."""
from pydantic import BaseModel


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    pages: int
    chunks: int | None = None


class DocumentList(BaseModel):
    documents: list[DocumentInfo]


class ChatRequest(BaseModel):
    question: str
    doc_ids: list[str] | None = None


class Citation(BaseModel):
    doc_id: str
    filename: str
    page: int
    snippet: str


class ToolUse(BaseModel):
    name: str
    input: str
    output: str


class ChatResponse(BaseModel):
    answer: str
    found: bool
    citations: list[Citation]
    tools_used: list[ToolUse]
