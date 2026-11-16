# API Routes Plan

Base URL (local): `http://127.0.0.1:8000` - interactive docs at `/docs` (Swagger UI).

| Method | Route | Purpose |
|---|---|---|
| POST | `/ingest` | Upload one PDF: extract text per page, chunk, embed (Ollama), store in ChromaDB |
| POST | `/ask` | Ask a question; streamed answer (SSE) with source citations |
| POST | `/ask/sync` | Same, but one JSON response |
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

## POST `/ask`  (streamed)
**Request**
```json
{ "question": "What is the wheel nut torque in lbf-ft?", "doc_ids": ["d_2d85baef"] }
```
`doc_ids` is optional; leave it out to search every ingested document.

**200 OK** - `Content-Type: text/event-stream` (Server-Sent Events). The answer arrives piece by piece:
```
event: token
data: {"text": "The wheel nut torque is "}

event: token
data: {"text": "108 Nm, about 79.66 lbf-ft [1]."}

event: final
data: {"found": true, "citations": [{"doc_id": "d_2d85baef", "filename": "falcon_x200_service_manual.pdf", "page": 3, "snippet": "..."}], "tools_used": [{"name": "unit_convert", "input": "108.0 nm -> lbf-ft", "output": "79.66"}]}

event: done
data: {}
```
**Not in the documents:** one `token` event with "I couldn't find this in the uploaded documents.", then `final` with `"found": false` and empty `citations`.

**Failure while streaming:** an `error` event (message explains Ollama may be down), then `done`.

Citations come from stored metadata (never invented by the model).

## POST `/ask/sync`
Same request, but returns one JSON object: `{ "answer", "found", "citations", "tools_used" }`. `503` if Ollama is unreachable. Handy for scripts and tests.

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
- `session_id` on `/ask` for follow-up questions
