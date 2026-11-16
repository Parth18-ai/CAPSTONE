"""Run: python -m evals.run_evals     (PDFs must be ingested first: python -m scripts.ingest_pdfs)"""
import json
import os
import time

from app.agent.graph import agent

rows = [json.loads(line) for line in open("evals/dataset.jsonl") if line.strip()]
res = {"hit": [], "correct": [], "tool": [], "refusal": []}
times, details = [], []

for r in rows:
    t = time.time()
    out = agent.invoke({"question": r["question"], "doc_ids": None})
    times.append(time.time() - t)
    answer = out["answer"].lower().replace("\u00a0", " ")
    used_tool = bool(out.get("tools_used"))

    if r["should_answer"]:
        hit = any(c["filename"] == r["expected_doc"] and c["page"] in r["expected_pages"]
                  for c in out.get("citations", []))
        correct = out["found"] and all(s.lower() in answer for s in r["must_contain"])
        tool_ok = used_tool == r["uses_tool"]
        res["hit"].append(hit); res["correct"].append(correct); res["tool"].append(tool_ok)
        details.append({"id": r["id"], "hit": hit, "correct": correct, "tool_ok": tool_ok})
    else:
        refused = out["found"] is False
        res["refusal"].append(refused)
        details.append({"id": r["id"], "refused": refused})
    print(f"Q{r['id']:>2} {details[-1]}  ({times[-1]:.1f}s)")


def pct(xs):
    return f"{sum(xs)}/{len(xs)}" if xs else "n/a"


print("\n=== Summary ===")
print("Citation hit (right doc + page):", pct(res["hit"]))
print("Answer correct (key fact found):", pct(res["correct"]))
print("Tool use as expected:           ", pct(res["tool"]))
print("Refusal on not-in-manual:       ", pct(res["refusal"]))
print(f"Average latency:                 {sum(times) / len(times):.1f}s")

os.makedirs("evals/results", exist_ok=True)
json.dump({"details": details}, open("evals/results/latest.json", "w"), indent=2)
