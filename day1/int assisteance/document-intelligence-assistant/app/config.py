"""All settings in one place. Values come from the .env file (or defaults)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "llama3.2"            # answers questions
    embed_model: str = "nomic-embed-text"  # turns text into vectors (also via Ollama)
    ollama_host: str = "http://localhost:11434"
    chroma_dir: str = "data/chroma"
    chunk_size: int = 800        # characters per chunk
    chunk_overlap: int = 100     # characters shared between neighbouring chunks
    top_k: int = 4               # how many chunks to retrieve
    max_distance: float = 0.6    # cosine distance; bigger = less similar. Tune this!

    model_config = {"env_file": ".env"}


settings = Settings()
