from pathlib import Path

from app.retrieval import Retriever, load_chunks, tokenize


def test_tokenize_normalizes_accents():
    assert "memoire" in tokenize("Dépassement mémoire")


def test_retriever_finds_kubernetes_runbook():
    retriever = Retriever(load_chunks(Path("runbooks")))
    matches = retriever.search("pod CrashLoopBackOff redémarre", top_k=2)
    assert matches
    assert matches[0].chunk.source == "kubernetes-crashloop.md"


def test_retriever_returns_nothing_for_unknown_subject():
    retriever = Retriever(load_chunks(Path("runbooks")))
    assert retriever.search("recette tarte fraises") == []
