# Task Board (Trello / Jira)

Columns: **Done** | **In Progress** | **To Do** | **Backlog**. Labels: foundation, ingestion, agent, api, evals, docs, ship.

**Jira:** Projects > Import issues > CSV > upload `docs/jira_import.csv`; map Summary, Issue Type, Priority, Status, Labels, Description.  

**Trello:** create 4 lists, then paste the lines of a column below into 'Add a card' - Trello offers to create one card per line.


## Done

- [api] Streamed POST /ask (SSE) with citations + /ask/sync (High)
- [foundation] Project scaffold: FastAPI app, config, Pydantic schemas (High)
- [foundation] Prepare 3 sample vehicle service manuals (PDF) (High)
- [ingestion] PDF loader, chunker and indexer (High)
- [ingestion] Ollama provider: chat (llama3.2) + embeddings (nomic-embed-text) (High)
- [agent] LangGraph agent: retrieve, grade, decide_tool, answer, not_found (High)
- [agent] unit_convert tool (Nm/lbf-ft, psi/bar, L/gal, km/mi) (Medium)
- [api] API routes: /ingest, /ask, /health (+ /documents list/delete) (High)
- [ingestion] Ingestion script on 3+ PDFs (scripts/ingest_pdfs.py) (High)
- [docs] Architecture diagram (Medium)
- [evals] Draft 20-question eval set (High)
- [evals] Smoke test: oil-grade question answered with page citation (Medium)

## In Progress

_(empty - move cards here as you start them)_

## To Do

- [ingestion] Run scripts.ingest_pdfs on all 3 PDFs on the local machine (High)
- [evals] Run baseline evals and record scores (High)
- [evals] Tune MAX_DISTANCE and TOP_K using eval results (High)
- [agent] Improve tool-use reliability of small local model (Medium)

## Backlog

- [agent] Add question rewriting for follow-up questions (session_id) (Medium)
- [evals] Expand eval set to 40 questions, add multi-chunk questions (Medium)
- [ship] Dockerfile and docker-compose (API + Ollama) (Medium)
- [ship] Simple web frontend (upload + chat + citations) (Low)
- [ingestion] OCR support for scanned PDFs (Low)
- [ship] API tests for /ingest, /ask, /health (Medium)
