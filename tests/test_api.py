from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

from unittest.mock import patch


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_analysis_state():

    # Reset analysis results before every test
    app.state.analysis_result = None

    yield

    # Clean up after every test
    app.state.analysis_result = None

def test_analyze_repository():

    repo_path = (
        Path(__file__).resolve().parents[1]
        / "sample_repos"
        / "graph_demo"
    )

    response = client.post(
        "/analyze",
        json={"repo_path": str(repo_path)}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_files"] == 3
    assert data["successful_files"] == 3
    assert data["failed_files"] == 0
    assert data["message"] == "Repository analysis completed"

def test_analyze_invalid_repository():

    response = client.post(
        "/analyze",
        json={"repo_path": "invalid_repository_path"}
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Repository path does not exist"
    }

def test_search_symbols():

    repo_path = (
        Path(__file__).resolve().parents[1]
        / "sample_repos"
        / "graph_demo"
    )

    # Analyze repository first
    client.post(
        "/analyze",
        json={"repo_path": str(repo_path)}
    )

    # Search for login function
    response = client.get(
        "/symbols",
        params={"name": "login"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "login"
    assert len(data["matches"]) == 2

    file_paths = [
        match["file_path"].replace("\\", "/")
        for match in data["matches"]
    ]

    assert any(path.endswith("auth.py") for path in file_paths)
    assert any(path.endswith("admin.py") for path in file_paths)

def test_find_callers():

    repo_path = (
        Path(__file__).resolve().parents[1]
        / "sample_repos"
        / "graph_demo"
    )

    # Analyze repository first
    client.post(
        "/analyze",
        json={"repo_path": str(repo_path)}
    )

    # Find callers of login
    response = client.get("/callers/login")

    assert response.status_code == 200

    data = response.json()

    assert data["function"] == "login"

    # Find the auth.py result
    auth_result = next(
        result for result in data["results"]
        if result["file_path"].replace("\\", "/").endswith("auth.py")
    )

    assert len(auth_result["callers"]) == 1

    assert auth_result["callers"][0]["name"] == "start_application"

def test_find_dependencies():

    repo_path = (
        Path(__file__).resolve().parents[1]
        / "sample_repos"
        / "graph_demo"
    )

    # Analyze repository first
    client.post(
        "/analyze",
        json={"repo_path": str(repo_path)}
    )

    # Find dependencies of start_application
    response = client.get(
        "/dependencies/start_application"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["function"] == "start_application"
    assert len(data["results"]) == 1

    dependencies = data["results"][0]["dependencies"]

    assert len(dependencies) == 1
    assert dependencies[0]["name"] == "login"

    assert dependencies[0]["file_path"].replace("\\", "/").endswith("auth.py")

def test_analyze_impact():

    repo_path = (
        Path(__file__).resolve().parents[1]
        / "sample_repos"
        / "graph_demo"
    )

    # Analyze repository first
    client.post(
        "/analyze",
        json={"repo_path": str(repo_path)}
    )

    # Find the impact of changing login
    response = client.get("/impact/login")

    assert response.status_code == 200

    data = response.json()

    assert data["function"] == "login"

    # Find the auth.py result
    auth_result = next(
        result for result in data["results"]
        if result["file_path"].replace("\\", "/").endswith("auth.py")
    )

    affected_functions = auth_result["affected_functions"]

    assert len(affected_functions) == 1
    assert affected_functions[0]["name"] == "start_application"

def test_search_symbols_before_analysis():

    response = client.get(
        "/symbols",
        params={"name": "login"}
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Analyze a repository first"
    }


def test_ask_question_success():

    mock_result = {
        "question": "Which login function does start_application call?",
        "answer": "It calls login() from auth.py.",
        "sources": [
            {
                "file_path": "sample_repos/graph_demo/auth.py",
                "symbol_name": "login",
                "start_line": 1,
                "end_line": 2,
                "similarity": 0.91
            }
        ]
    }

    with patch(
        "app.main.qa_service.answer_question",
        return_value=mock_result
    ) as mock_qa:

        response = client.post(
            "/ask",
            json={
                "repository_id": 3,
                "question": "Which login function does start_application call?",
                "top_k": 5
            }
        )

    assert response.status_code == 200
    assert response.json() == mock_result

    mock_qa.assert_called_once_with(
        repository_id=3,
        question="Which login function does start_application call?",
        top_k=5
    )

def test_ask_question_handles_error():

    with patch(
        "app.main.qa_service.answer_question",
        side_effect=Exception("Gemini API failed")
    ):

        response = client.post(
            "/ask",
            json={
                "repository_id": 3,
                "question": "Explain the login function",
                "top_k": 5
            }
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to generate answer"
    }


def test_ask_question_missing_question():

    response = client.post(
        "/ask",
        json={
            "repository_id": 3,
            "top_k": 5
        }
    )

    assert response.status_code == 422
