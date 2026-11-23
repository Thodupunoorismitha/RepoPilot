from app.analyzer.scanner import RepositoryScanner
from app.graph.symbol_table import SymbolTable


def test_add_symbol():

    table = SymbolTable()

    table.add_symbol("login", "auth.py:login")

    result = table.find_symbols("login")

    assert result == ["auth.py:login"]


def test_handle_duplicate_function_names():

    table = SymbolTable()

    table.add_symbol("login", "auth.py:login")
    table.add_symbol("login", "admin.py:login")

    result = table.find_symbols("login")

    assert len(result) == 2
    assert "auth.py:login" in result
    assert "admin.py:login" in result


def test_find_nonexistent_symbol():

    table = SymbolTable()

    result = table.find_symbols("logout")

    assert result == []


def test_build_symbol_table_from_scan_results():

    table = SymbolTable()

    scan_results = [
        {
            "file_path": "auth.py",
            "status": "success",
            "analysis": {
                "functions": [
                    {
                        "name": "login",
                        "start_line": 1,
                        "end_line": 3
                    }
                ]
            }
        },
        {
            "file_path": "admin.py",
            "status": "success",
            "analysis": {
                "functions": [
                    {
                        "name": "login",
                        "start_line": 1,
                        "end_line": 3
                    }
                ]
            }
        },
        {
            "file_path": "broken.py",
            "status": "error",
            "error": "Invalid syntax"
        }
    ]

    table.build_from_scan_results(scan_results)

    result = table.find_symbols("login")

    assert len(result) == 2
    assert "auth.py:login" in result
    assert "admin.py:login" in result


def test_symbol_table_with_real_repository_scanner():

    scanner = RepositoryScanner()
    table = SymbolTable()

    repo_path = "sample_repos/graph_demo"

    # Scan the actual repository
    scan_results = scanner.scan(repo_path)

    # Build the symbol table
    table.build_from_scan_results(scan_results)

    # Check duplicate login definitions
    login_definitions = table.find_symbols("login")

    assert len(login_definitions) == 2

    # Check that both files are represented
    assert any("auth.py:login" in item for item in login_definitions)
    assert any("admin.py:login" in item for item in login_definitions)

    # Check another function
    start_definitions = table.find_symbols("start_application")

    assert len(start_definitions) == 1
