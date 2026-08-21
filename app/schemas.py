from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    engine: Literal["auto", "ollama", "extractive"] = "auto"
    top_k: int = Field(default=3, ge=1, le=5)


class Citation(BaseModel):
    title: str
    source: str
    section: str
    excerpt: str
    score: float


class QueryResponse(BaseModel):
    summary: str
    checks: list[str]
    commands: list[str]
    warnings: list[str]
    citations: list[Citation]
    confidence: float = Field(ge=0, le=1)
    engine: str
    model: str | None = None
    duration_ms: int
    redactions: int = 0


class RunbookInfo(BaseModel):
    title: str
    source: str
    sections: int
