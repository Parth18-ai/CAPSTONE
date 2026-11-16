# Document Intelligence Assistant

Upload PDFs (e.g. vehicle service manuals), ask questions, get answers with page citations.
Everything runs locally on Ollama (no API keys). A LangGraph agent retrieves from ChromaDB, uses a unit-converter tool when needed, and says
"couldn't find this" instead of guessing.

## Run it
```bash
ollama pull llama3.2            # chat model: writes answers (needs Ollama installed and running)
ollama pull nomic-embed-text    # embedding model: turns text into searchable vectors
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs (Swagger UI) -> `POST /documents` to upload a PDF -> `POST /chat` to ask.

Or with curl:
```bash
curl -F "file=@data/pdfs/manual.pdf" localhost:8000/documents
curl -X POST localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"question": "What is the front wheel nut torque in lbf-ft?"}'
```

## Test and evaluate
```bash
pytest
python -m evals.run_evals
```
