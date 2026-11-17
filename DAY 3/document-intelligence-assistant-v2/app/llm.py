"""Talks to Ollama over HTTP (embeddings + chat)."""
import requests

from . import config


def embed(texts: list) -> list:
    vectors = []
    for i in range(0, len(texts), 32):  # small batches
        r = requests.post(f"{config.OLLAMA_URL}/api/embed",
                          json={"model": config.EMBED_MODEL, "input": texts[i:i + 32]},
                          timeout=300)
        r.raise_for_status()
        vectors.extend(r.json()["embeddings"])
    return vectors


def chat(system: str, user: str) -> dict:
    r = requests.post(f"{config.OLLAMA_URL}/api/chat",
                      json={"model": config.CHAT_MODEL, "stream": False,
                            "options": {"temperature": 0},
                            "messages": [{"role": "system", "content": system},
                                         {"role": "user", "content": user}]},
                      timeout=600)
    r.raise_for_status()
    d = r.json()
    return {"text": d["message"]["content"].strip(),
            "prompt_tokens": d.get("prompt_eval_count"),
            "completion_tokens": d.get("eval_count")}
