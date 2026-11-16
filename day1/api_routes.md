# API Routes Plan

Base URL (local): `http://127.0.0.1:8000` - interactive docs at `/docs` (Swagger UI).

| Method | Route | Purpose |
|---|---|---|
| POST | `/ingest` | Upload one PDF: extract text per page, chunk, embed (Ollama), store in ChromaDB |
| POST | `/ask` | Ask a question; the LangGraph agent retrieves, optionally uses a tool, answers with citations |
| GET | `/health` | Is the API up, is Ollama reachable, how many documents are stored |
| GET | `/documents` | (supporting) list ingested documents |
| DELETE | `/documents/{doc_id}` | (supporting) remove a document and its chunks |

---

## POST `/ingest`
**Request:** `multipart/form-data` with one field `file` (a `.pdf`).

**201 Created**
```json
{ "doc_id": "d_2d85baef", "filename": "falcon_x200_service_manual.pdf", "pages": 8, "chunks": 12 }
```
**Errors:** `400` not a PDF - `409` a file with this name is already ingested - `422` missing file - `500` extraction/embedding failure (Ollama not running).

**What happens inside:** load PDF (page by page) -> chunk (800 chars, 100 overlap) -> embed each chunk with `nomic-embed-text` -> store in ChromaDB with metadata `doc_id`, `filename`, `page`.

Bulk alternative (no HTTP): `python -m scripts.ingest_pdfs` ingests every PDF in `data/pdfs/`.

---

## POST `/ask`
**Request**
```json
{
  "question": "What is the wheel nut torque in lbf-ft?",
  "doc_ids": ["d_2d85baef"]
}
```
`doc_ids` is optional; leave it out to search every ingested document.

**200 OK - answer found**
```json
{
  "answer": "The wheel nut torque is 108 Nm, about 79.66 lbf-ft [1].",
  "found": true,
  "citations": [
    { "doc_id": "d_2d85baef", "filename": "falcon_x200_service_manual.pdf", "page": 3,
      "snippet": "Wheel nuts 108 Nm ..." }
  ],
  "tools_used": [ { "name": "unit_convert", "input": "108.0 nm -> lbf-ft", "output": "79.66" } ]
}
```
**200 OK - not in the documents**
```json
{ "answer": "I couldn't find this in the uploaded documents.", "found": false, "citations": [], "tools_used": [] }
```
**Errors:** `422` missing/invalid `question` - `500` Ollama not reachable.

Rules: citations come from stored metadata (never invented by the model); `found=false` means no chunk passed the similarity threshold (`MAX_DISTANCE`).

---

## GET `/health`
**200 OK**
```json
{ "status": "ok", "ollama": true, "documents": 3 }
```
`status` is `"degraded"` (and `ollama` is `false`) when Ollama cannot be reached. Used for manual checks and, later, Docker health checks.

---

## GET `/documents` and DELETE `/documents/{doc_id}`
- `GET /documents` -> `{ "documents": [ { "doc_id", "filename", "pages", "chunks" } ] }`
- `DELETE /documents/{doc_id}` -> `204 No Content`, or `404` for an unknown `doc_id`.

## Planned later (not built yet)
- `POST /ask/stream` - streaming answers (SSE)
- `session_id` on `/ask` for follow-up questions
