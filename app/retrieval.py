from collections import Counter
from dataclasses import dataclass
import math
from pathlib import Path
import re
import unicodedata


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]+")
STOP_WORDS = {
    "avec", "cette", "comment", "dans", "des", "est", "les", "pour", "que", "qui",
    "sur", "un", "une", "the", "and", "from", "this", "what", "when",
}
QUERY_EXPANSIONS = {
    "diagnostic": ("verifications",),
    "diagnostiquer": ("verifications",),
    "verifier": ("verifications",),
}


@dataclass(frozen=True)
class Chunk:
    title: str
    source: str
    section: str
    content: str


@dataclass(frozen=True)
class Match:
    chunk: Chunk
    score: float


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return [token for token in TOKEN_RE.findall(normalized) if token not in STOP_WORDS]


def load_chunks(root: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = path.stem.replace("-", " ").title()
        section = "Introduction"
        buffer: list[str] = []
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                continue
            if line.startswith("## "):
                _append_chunk(chunks, title, root, path, section, buffer)
                section = line[3:].strip()
                buffer = []
            else:
                buffer.append(line)
        _append_chunk(chunks, title, root, path, section, buffer)
    return chunks


def _append_chunk(chunks: list[Chunk], title: str, root: Path, path: Path, section: str, lines: list[str]) -> None:
    content = "\n".join(lines).strip()
    if content:
        chunks.append(Chunk(title, path.relative_to(root).as_posix(), section, content))


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.documents = [Counter(tokenize(chunk.content + " " + chunk.section)) for chunk in chunks]
        self.document_frequency = Counter()
        for document in self.documents:
            self.document_frequency.update(document.keys())

    def search(self, query: str, top_k: int = 3) -> list[Match]:
        query_terms = Counter(tokenize(query))
        for term in list(query_terms):
            query_terms.update(QUERY_EXPANSIONS.get(term, ()))
        scores: list[Match] = []
        total = max(len(self.documents), 1)
        for chunk, document in zip(self.chunks, self.documents):
            score = 0.0
            title_terms = set(tokenize(chunk.title))
            title_bonus = 0.0
            for term, query_frequency in query_terms.items():
                if term in title_terms:
                    title_bonus += 2.0 * query_frequency
                if term not in document:
                    continue
                inverse_frequency = math.log((total + 1) / (self.document_frequency[term] + 1)) + 1
                score += min(document[term], 3) * query_frequency * inverse_frequency
            if score or title_bonus:
                normalized = score / math.sqrt(max(sum(document.values()), 1)) + title_bonus
                scores.append(Match(chunk, round(normalized, 4)))
        return sorted(scores, key=lambda item: item.score, reverse=True)[:top_k]
