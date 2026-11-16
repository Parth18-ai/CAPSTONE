"""Everything that talks to Ollama: chat model (answers) + embedding model (search vectors)."""
import ollama

from app.config import settings


class OllamaProvider:
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_host)

    def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        res = self.client.chat(
            model=settings.llm_model,
            messages=messages,
            format="json" if json_mode else None,
            options={"temperature": 0},
        )
        return res["message"]["content"]

    def embed(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
        """Turn texts into vectors. nomic-embed-text works best with these prefixes."""
        prefix = "search_query: " if is_query else "search_document: "
        vectors = []
        for i in range(0, len(texts), 32):  # small batches so big PDFs don't overload Ollama
            batch = [prefix + t for t in texts[i:i + 32]]
            vectors += self.client.embed(model=settings.embed_model, input=batch)["embeddings"]
        return vectors


def get_llm() -> OllamaProvider:
    return OllamaProvider()
