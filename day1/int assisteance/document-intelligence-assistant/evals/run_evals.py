"""Run: python -m evals.run_evals   (edit dataset.jsonl with real questions + pages first)"""
import json
import time

from app.agent.graph import agent

rows = [json.loads(line) for line in open("evals/dataset.jsonl") if line.strip()]
hits = refusals_ok = answerable = unanswerable = 0
times = []

for r in rows:
    t = time.time()
    out = agent.invoke({"question": r["question"], "doc_ids": None})
    times.append(time.time() - t)
    if r["should_answer"]:
        answerable += 1
        pages = [c["page"] for c in out.get("citations", [])]
        hits += r["expected_page"] in pages
    else:
        unanswerable += 1
        refusals_ok += (out["found"] is False)

print(f"Citation page hit rate: {hits}/{answerable}")
print(f"Refusal accuracy:       {refusals_ok}/{unanswerable}")
print(f"Avg latency:            {sum(times)/len(times):.1f}s")
