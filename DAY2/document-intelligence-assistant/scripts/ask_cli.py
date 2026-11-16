"""Watch the streamed answer arrive live in the terminal.

Usage (server must be running):
    python -m scripts.ask_cli "What engine oil grade does the Nomad T300 need?"
    python -m scripts.ask_cli "..." --doc d_2d85baef        # search one document only
"""
import argparse
import json
import sys
import urllib.error
import urllib.request


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--doc", action="append", help="doc_id to search (repeatable)")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    body = json.dumps({"question": args.question, "doc_ids": args.doc}).encode()
    req = urllib.request.Request(args.url + "/ask", data=body, headers={"Content-Type": "application/json"})
    event = None
    try:
        with urllib.request.urlopen(req) as resp:
            for raw in resp:
                line = raw.decode("utf-8").rstrip("\r\n")
                if line.startswith("event:"):
                    event = line[6:].strip()
                elif line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if event == "token":
                        print(data["text"], end="", flush=True)
                    elif event == "final":
                        print(f"\n\nfound: {data['found']}")
                        for c in data["citations"]:
                            print(f"  source: {c['filename']}, page {c['page']}")
                        for t in data["tools_used"]:
                            print(f"  tool: {t['name']} ({t['input']} = {t['output']})")
                    elif event == "error":
                        print(f"\nERROR: {data['message']}")
                        return 1
    except urllib.error.URLError as e:
        print(f"Could not reach the server at {args.url}: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
