from app.graph.dependency_graph import DependencyGraphBuilder
from app.graph.symbol_table import SymbolTable
from app.analyzer.scanner import RepositoryScanner

def test_add_function_node():

    builder = DependencyGraphBuilder()

    function = {
        "name": "login",
        "calls": [],
        "start_line": 10,
        "end_line": 15
    }

    node_id = builder.add_function_node("auth.py", function)

    # Check the unique node identifier
    assert node_id == "auth.py:login"

    # Check that the node exists
    assert "auth.py:login" in builder.graph.nodes

    # Check node attributes
    node_data = builder.graph.nodes["auth.py:login"]

    assert node_data["name"] == "login"
    assert node_data["file_path"] == "auth.py"
    assert node_data["start_line"] == 10
    assert node_data["end_line"] == 15
    assert node_data["type"] == "function"


def test_add_multiple_functions():

    builder = DependencyGraphBuilder()

    functions = [
        {
            "name": "login",
            "calls": [],
            "start_line": 1,
            "end_line": 2
        },
        {
            "name": "dashboard",
            "calls": ["login"],
            "start_line": 4,
            "end_line": 6
        },
        {
            "name": "logout",
            "calls": [],
            "start_line": 8,
            "end_line": 9
        }
    ]

    node_ids = builder.add_functions_from_file("auth.py", functions)

    assert len(node_ids) == 3
    assert builder.graph.number_of_nodes() == 3

    assert "auth.py:login" in builder.graph.nodes
    assert "auth.py:dashboard" in builder.graph.nodes
    assert "auth.py:logout" in builder.graph.nodes


def test_add_call_edge():

    builder = DependencyGraphBuilder()

    # Create two function nodes
    caller = {
        "name": "dashboard",
        "calls": ["login"],
        "start_line": 4,
        "end_line": 6
    }

    called = {
        "name": "login",
        "calls": [],
        "start_line": 1,
        "end_line": 2
    }

    caller_id = builder.add_function_node("auth.py", caller)
    called_id = builder.add_function_node("auth.py", called)

    # Create the relationship
    builder.add_call_edge(
        caller_id,
        called_id,
        line_number=5
    )

    # Verify the edge
    assert builder.graph.has_edge(caller_id, called_id)

    edge_data = builder.graph.edges[caller_id, called_id]

    assert edge_data["relationship"] == "calls"
    assert edge_data["line_number"] == 5

    # Verify direction
    assert list(builder.graph.predecessors(called_id)) == [caller_id]
    assert list(builder.graph.successors(caller_id)) == [called_id]


def test_build_cross_file_edges():

    # Step 1: Scan the sample repository
    scanner = RepositoryScanner()
    scan_results = scanner.scan("sample_repos/graph_demo")
    for item in scan_results:
        if item["status"] == "success":
            print("\nFILE:", item["file_path"])
            print("IMPORTS:", item["analysis"]["imports"])
            print("FUNCTIONS:", item["analysis"]["functions"])

    # Step 2: Build the symbol table
    symbol_table = SymbolTable()
    symbol_table.build_from_scan_results(scan_results)

    print("\nSYMBOL TABLE:", symbol_table.symbols)

    # Step 3: Create the dependency graph
    builder = DependencyGraphBuilder()

    # Step 4: Create nodes for all functions
    for file_result in scan_results:

        if file_result["status"] != "success":
            continue

        file_path = file_result["file_path"]
        functions = file_result["analysis"]["functions"]

        builder.add_functions_from_file(file_path, functions)

    # Step 5: Build cross-file edges
    builder.build_cross_file_edges(scan_results, symbol_table)
    print("\nGRAPH EDGES:", list(builder.graph.edges))

    # Step 6: Verify the cross-file relationship
    caller_id = "sample_repos/graph_demo/main.py:start_application"
    called_id = "sample_repos/graph_demo/auth.py:login"

    print("Actual graph nodes:", list(builder.graph.nodes))
    print("Expected caller ID:", caller_id)

    assert builder.graph.has_edge(caller_id, called_id)

    edge_data = builder.graph.edges[caller_id, called_id]

    assert edge_data["relationship"] == "calls"


def test_build_same_file_edges():

    functions = [
        {
            "name": "add",
            "calls": [],
            "start_line": 1,
            "end_line": 2
        },
        {
            "name": "multiply",
            "calls": [],
            "start_line": 4,
            "end_line": 5
        },
        {
            "name": "main",
            "calls": ["add", "multiply"],
            "start_line": 7,
            "end_line": 10
        }
    ]

    file_path = "sample_repos/calculator.py"

    builder = DependencyGraphBuilder()

    # Step 1: Create function nodes
    builder.add_functions_from_file(file_path, functions)

    # Step 2: Create dependency edges
    builder.build_edges(functions, file_path)

    # Step 3: Verify expected edges
    caller_id = "sample_repos/calculator.py:main"
    add_id = "sample_repos/calculator.py:add"
    multiply_id = "sample_repos/calculator.py:multiply"

    assert builder.graph.has_edge(caller_id, add_id)
    assert builder.graph.has_edge(caller_id, multiply_id)

    assert builder.graph.number_of_edges() == 2


def create_graph_from_repository(repo_path):

    scanner = RepositoryScanner()
    scan_results = scanner.scan(str(repo_path))

    symbol_table = SymbolTable()
    symbol_table.build_from_scan_results(scan_results)

    builder = DependencyGraphBuilder()

    for file_result in scan_results:

        if file_result["status"] != "success":
            continue

        file_path = file_result["file_path"]
        functions = file_result["analysis"]["functions"]

        builder.add_functions_from_file(file_path, functions)

    builder.build_cross_file_edges(scan_results, symbol_table)

    return builder


def test_from_import_without_alias(tmp_path):

    # Create auth.py
    auth_file = tmp_path / "auth.py"
    auth_file.write_text(
        "def login():\n"
        "    print('User logged in')\n"
    )

    # Create main.py
    main_file = tmp_path / "main.py"
    main_file.write_text(
        "from auth import login\n\n"
        "def start_application():\n"
        "    login()\n"
    )

    # Build the dependency graph
    builder = create_graph_from_repository(tmp_path)

    caller_id = f"{main_file.as_posix()}:start_application"
    called_id = f"{auth_file.as_posix()}:login"

    assert builder.graph.has_edge(caller_id, called_id)


def test_from_import_with_alias(tmp_path):

    # Create auth.py
    auth_file = tmp_path / "auth.py"
    auth_file.write_text(
        "def login():\n"
        "    print('User logged in')\n"
    )

    # Create main.py
    main_file = tmp_path / "main.py"
    main_file.write_text(
        "from auth import login as user_login\n\n"
        "def start_application():\n"
        "    user_login()\n"
    )

    # Build the dependency graph
    builder = create_graph_from_repository(tmp_path)

    caller_id = f"{main_file.as_posix()}:start_application"
    called_id = f"{auth_file.as_posix()}:login"

    assert builder.graph.has_edge(caller_id, called_id)


def test_module_import_without_alias(tmp_path):

    # Create auth.py
    auth_file = tmp_path / "auth.py"
    auth_file.write_text(
        "def login():\n"
        "    print('User logged in')\n"
    )

    # Create main.py
    main_file = tmp_path / "main.py"
    main_file.write_text(
        "import auth\n\n"
        "def start_application():\n"
        "    auth.login()\n"
    )

    # Build the dependency graph
    builder = create_graph_from_repository(tmp_path)

    caller_id = f"{main_file.as_posix()}:start_application"
    called_id = f"{auth_file.as_posix()}:login"

    assert builder.graph.has_edge(caller_id, called_id)


def test_module_import_with_alias(tmp_path):

    # Create auth.py
    auth_file = tmp_path / "auth.py"
    auth_file.write_text(
        "def login():\n"
        "    print('User logged in')\n"
    )

    # Create main.py
    main_file = tmp_path / "main.py"
    main_file.write_text(
        "import auth as authentication\n\n"
        "def start_application():\n"
        "    authentication.login()\n"
    )

    # Build the dependency graph
    builder = create_graph_from_repository(tmp_path)

    caller_id = f"{main_file.as_posix()}:start_application"
    called_id = f"{auth_file.as_posix()}:login"

    assert builder.graph.has_edge(caller_id, called_id)
