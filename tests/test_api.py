from fastapi.testclient import TestClient

from app.main import app


def test_health_and_runbooks():
    with TestClient(app) as client:
        health = client.get("/health")
        runbooks = client.get("/api/runbooks")
    assert health.status_code == 200
    assert health.json()["chunks"] >= 3
    assert runbooks.status_code == 200
    assert len(runbooks.json()) == 3


def test_extractive_query_has_citations():
    with TestClient(app) as client:
        response = client.post(
            "/api/query",
            json={"question": "Comment diagnostiquer un CrashLoopBackOff ?", "engine": "extractive"},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["engine"] == "extractive"
    assert payload["citations"]
    assert any("kubectl" in command for command in payload["commands"])


def test_unknown_query_admits_missing_context():
    with TestClient(app) as client:
        response = client.post(
            "/api/query",
            json={"question": "Comment préparer une tarte aux fraises ?", "engine": "extractive"},
        )
    assert response.status_code == 200
    assert response.json()["confidence"] == 0
