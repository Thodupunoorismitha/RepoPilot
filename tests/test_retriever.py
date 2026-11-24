
from app.retrieval.retriever import CodeRetriever


def test_retrieve_matching_chunks(monkeypatch):

    retriever = CodeRetriever()

    sample_chunks = [
        {
            "symbol_name": "login",
            "file_path": "auth.py",
            "start_line": 1,
            "end_line": 5,
            "content": 'def login():\n    print("Login successful")',
        },
        {
            "symbol_name": "start_application",
            "file_path": "main.py",
            "start_line": 1,
            "end_line": 3,
            "content": "def start_application():\n    login()",
        }
    ]

    monkeypatch.setattr(
        retriever.chunk_db,
        "get_chunks_by_repository",
        lambda repository_id: sample_chunks
    )

    results = retriever.retrieve(
        repository_id=1,
        query="login functionality"
    )

    assert len(results) == 2

    # Direct implementation should rank higher
    assert results[0]["symbol_name"] == "login"
    assert results[0]["score"] > results[1]["score"]

    # Cosine similarity must be between 0 and 1
    assert 0 <= results[0]["score"] <= 1
    assert 0 <= results[1]["score"] <= 1

def test_retrieve_no_matching_chunks(monkeypatch):

    retriever = CodeRetriever()

    monkeypatch.setattr(
        retriever.chunk_db,
        "get_chunks_by_repository",
        lambda repository_id: []
    )

    results = retriever.retrieve(
        repository_id=1,
        query="password validation"
    )

    assert results == []


def test_retrieve_respects_top_k(monkeypatch):

    retriever = CodeRetriever()

    sample_chunks = [
        {
            "symbol_name": f"login_{i}",
            "file_path": f"file_{i}.py",
            "start_line": 1,
            "end_line": 3,
            "content": "def login(): pass",
        }
        for i in range(5)
    ]

    monkeypatch.setattr(
        retriever.chunk_db,
        "get_chunks_by_repository",
        lambda repository_id: sample_chunks
    )

    results = retriever.retrieve(
        repository_id=1,
        query="login",
        top_k=2
    )

    assert len(results) == 2
