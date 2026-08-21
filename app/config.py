from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    rag_engine: str = os.getenv("RAG_ENGINE", "auto")
    runbooks_path: Path = Path(os.getenv("RUNBOOKS_PATH", "runbooks"))
    max_question_length: int = int(os.getenv("MAX_QUESTION_LENGTH", "2000"))


settings = Settings()
