from contextlib import asynccontextmanager
from pathlib import Path
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx

from app.config import settings
from app.generator import extractive_answer, ollama_answer
from app.redaction import redact
from app.retrieval import Retriever, load_chunks
from app.schemas import Citation, QueryRequest, QueryResponse, RunbookInfo


@asynccontextmanager
async def lifespan(app: FastAPI):
    chunks = load_chunks(settings.runbooks_path)
    app.state.chunks = chunks
    app.state.retriever = Retriever(chunks)
    yield


app = FastAPI(title="Local Runbook RAG", version="0.1.0", lifespan=lifespan)
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(static_path / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "chunks": len(app.state.chunks)}


@app.get("/api/runbooks", response_model=list[RunbookInfo])
async def runbooks():
    grouped: dict[tuple[str, str], int] = {}
    for chunk in app.state.chunks:
        key = (chunk.title, chunk.source)
        grouped[key] = grouped.get(key, 0) + 1
    return [RunbookInfo(title=key[0], source=key[1], sections=count) for key, count in grouped.items()]


@app.post("/api/query", response_model=QueryResponse)
async def query(payload: QueryRequest):
    started = time.perf_counter()
    question, redactions = redact(payload.question)
    matches = app.state.retriever.search(question, payload.top_k)
    requested_engine = payload.engine if payload.engine != "auto" else settings.rag_engine
    result = None
    engine = "extractive"
    model = None
    if requested_engine in {"auto", "ollama"} and matches:
        try:
            result = await ollama_answer(matches, question, settings.ollama_base_url, settings.ollama_model)
            engine, model = "ollama", settings.ollama_model
        except (httpx.HTTPError, KeyError, ValueError):
            if payload.engine == "ollama":
                raise HTTPException(503, "Ollama est indisponible ou a retourné une réponse invalide.")
    if result is None:
        result = extractive_answer(matches)
    citations = [
        Citation(
            title=match.chunk.title,
            source=match.chunk.source,
            section=match.chunk.section,
            excerpt=" ".join(match.chunk.content.split())[:320],
            score=match.score,
        )
        for match in matches
    ]
    return QueryResponse(
        **result,
        citations=citations,
        engine=engine,
        model=model,
        duration_ms=round((time.perf_counter() - started) * 1000),
        redactions=redactions,
    )
