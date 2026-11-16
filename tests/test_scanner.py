
from app.analyzer.scanner import RepositoryScanner


def test_scanner_discovers_python_files(tmp_path):
    # Create a temporary repository
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    # Create Python files
    (repo / "main.py").write_text(
        "def main():\n    pass\n",
        encoding="utf-8"
    )

    nested = repo / "utils"
    nested.mkdir()

    (nested / "helper.py").write_text(
        "def helper():\n    pass\n",
        encoding="utf-8"
    )

    # Create scanner
    scanner = RepositoryScanner()

    # Scan repository
    results = scanner.scan(str(repo))

    # Verify discovered files
    assert len(results) == 2

    file_names = [
        result["file_path"].split("\\")[-1]
        for result in results
    ]

    assert "main.py" in file_names
    assert "helper.py" in file_names


def test_scanner_ignores_unnecessary_directories(tmp_path):
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    # Create a valid Python file
    (repo / "main.py").write_text(
        "print('Hello')",
        encoding="utf-8"
    )

    # Create directories that should be ignored
    for directory in [".venv", ".git", "__pycache__"]:
        ignored_folder = repo / directory
        ignored_folder.mkdir()

        (ignored_folder / "ignored.py").write_text(
            "print('Should be ignored')",
            encoding="utf-8"
        )

    scanner = RepositoryScanner()
    results = scanner.scan(str(repo))

    # Only main.py should be discovered
    assert len(results) == 1
    assert results[0]["file_path"].endswith("main.py")


def test_scanner_handles_syntax_errors(tmp_path):
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    # Create a valid Python file
    (repo / "valid.py").write_text(
        "def hello():\n    print('Hello')\n",
        encoding="utf-8"
    )

    # Create an invalid Python file
    (repo / "broken.py").write_text(
        "def calculate_area(\n",
        encoding="utf-8"
    )

    # Create scanner and scan repository
    scanner = RepositoryScanner()
    results = scanner.scan(str(repo))

    # Verify that both files were processed
    assert len(results) == 2

    # Find the results by filename
    valid_result = next(
        item for item in results
        if item["file_path"].endswith("valid.py")
    )

    broken_result = next(
        item for item in results
        if item["file_path"].endswith("broken.py")
    )

    # Verify successful parsing
    assert valid_result["status"] == "success"

    # Verify syntax error was captured
    assert broken_result["status"] == "error"
    assert "SyntaxError" in broken_result["error"] or "never closed" in broken_result["error"]


def test_scanner_handles_encoding_errors(tmp_path):
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    # Create a valid Python file
    (repo / "valid.py").write_text(
        "def hello():\n    pass\n",
        encoding="utf-8"
    )

    # Create a file containing invalid UTF-8 bytes
    (repo / "invalid_encoding.py").write_bytes(
        b"\xff\xfe\xfa"
    )

    scanner = RepositoryScanner()
    results = scanner.scan(str(repo))

    assert len(results) == 2

    invalid_result = next(
        item for item in results
        if item["file_path"].endswith("invalid_encoding.py")
    )

    valid_result = next(
        item for item in results
        if item["file_path"].endswith("valid.py")
    )

    assert invalid_result["status"] == "error"
    assert invalid_result["error_type"] == "UnicodeDecodeError"

    assert valid_result["status"] == "success"
