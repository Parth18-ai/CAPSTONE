# Document Intelligence Assistant (v2)

Upload PDFs, ask questions, get answers with sources. Runs fully local (Ollama + ChromaDB).
UI: Streamlit. Backend: FastAPI. Includes prompt-injection guard, cost/latency logging and an eval runner.

## One-time setup
```
pip install -r requirements.txt
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Run (3 terminals, all from this project folder)
1. Backend:  `uvicorn app.main:app --reload --port 8000`   (check http://localhost:8000/docs)
2. UI:       `streamlit run streamlit_app.py`
3. Evals:    `python evals/run_evals.py`

## Folder guide
- app/main.py       API routes: /health /ingest /ask /metrics
- app/rag.py        guard -> retrieve -> prompt -> LLM -> log
- app/ingest.py     PDF -> chunks -> embeddings -> ChromaDB
- app/guard.py      prompt-injection protection
- app/metrics.py    cost + latency logging (logs/requests.jsonl)
- app/config.py     tuning knobs: CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, MAX_DISTANCE
- evals/            evals.json (edit it!) + run_evals.py
- scripts/ingest_folder.py   re-ingest all PDFs in data/pdfs after changing chunk settings

## Tuning loop
1. `python evals/run_evals.py` -> note AVERAGE SCORE and the WEAKEST 5.
2. Change ONE setting in .env (copy .env.example to .env), e.g. TOP_K=6 or CHUNK_SIZE=1000.
3. If you changed CHUNK_SIZE or CHUNK_OVERLAP: `python scripts/ingest_folder.py`.
4. Restart uvicorn, run the evals again, keep the change only if the score goes up.
