import pytest
from tools.retrieval_tool import run
from grounding.vector_store.ingest import ingest_directory
from grounding.graph_store.kuzu_client import KuzuGraphStore

@pytest.fixture(scope="session", autouse=True)
def setup_databases():
    # Automatically prepares ChromaDB & KuzuDB before tests run
    ingest_directory("data/sops")
    kg = KuzuGraphStore()
    kg.seed_initial_data()

def test_retrieve_returns_relevant_chunks():
    result = run({"query": "pressure tolerance Valve V-204", "top_k": 3})
    assert result.success is True
    assert "chunks" in result.data
    assert len(result.data["chunks"]) > 0
    assert all("score" in c for c in result.data["chunks"])
    assert any("V-204" in c["text"] for c in result.data["chunks"])

def test_verify_claim_supported_and_unsupported():
    chunks = [
        {"text": "Valve V-204 rated tolerance is ±0.1 bar per SOP-114.", "source": "SOP-114.txt", "score": 0.9}
    ]
    supported = run({"claim": "Valve V-204 tolerance is 0.1 bar", "chunks": chunks})
    assert supported.success is True
    assert supported.data["supported"] is True

    unsupported = run({"claim": "Valve V-204 was manufactured in Germany in 1995", "chunks": chunks})
    assert unsupported.success is True
    assert unsupported.data["supported"] is False

def test_tool_failure_handling():
    """Proves Ground Rule 1: Bad input returns success=False without crashing."""
    result = run({"invalid_key": "some_value"})
    assert result.success is False
    assert result.error is not None