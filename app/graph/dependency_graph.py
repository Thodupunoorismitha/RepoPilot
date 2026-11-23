import networkx as nx
from pathlib import Path
from app.graph.symbol_table import SymbolTable

class DependencyGraphBuilder:

    def __init__(self):
        # Create an empty directed graph
        self.graph = nx.DiGraph()

    def add_function_node(self, file_path, function):
        """
        Add a function as a node in the dependency graph.
        """

        # Create a unique identifier
        normalized_path = Path(file_path).as_posix()
        node_id = f"{normalized_path}:{function['name']}"

        # Add the function and its metadata
        self.graph.add_node(
            node_id,
            name=function["name"],
            file_path=file_path,
            start_line=function["start_line"],
            end_line=function["end_line"],
            type="function"
        )

        return node_id


    def add_functions_from_file(self, file_path, functions):
        """
        Add all top-level functions from a Python file.
        """

        node_ids = []

        for function in functions:
            node_id = self.add_function_node(file_path, function)
            node_ids.append(node_id)

        return node_ids

    
    def add_call_edge(self, caller_id, called_id, line_number=None):
        """
        Add a directed edge representing a function call.
        """

        self.graph.add_edge(
            caller_id,
            called_id,
            relationship="calls",
            line_number=line_number
        )
    
    def build_edges(self, functions, file_path):
        """
        Create edges between functions based on their calls.
        """

        normalized_path = Path(file_path).as_posix()

        for function in functions:

            caller_id = f"{normalized_path}:{function['name']}"

            for called_function in function["calls"]:

                called_id = f"{normalized_path}:{called_function}"

                if caller_id in self.graph and called_id in self.graph:

                    self.add_call_edge(
                        caller_id,
                        called_id
                    )
    
    
    def build_cross_file_edges(self, scan_results, symbol_table):
        """
        Build dependency edges using import information
        and repository-wide symbol lookup.
        """

        module_to_file = {}

        # First pass: Build module-to-file mapping
        for file_result in scan_results:

            if file_result["status"] != "success":
                continue

            file_path = Path(file_result["file_path"]).as_posix()
            module_name = Path(file_path).stem

            module_to_file[module_name] = file_path

        # Second pass: Resolve function calls
        for file_result in scan_results:

            if file_result["status"] != "success":
                continue

            file_path = Path(file_result["file_path"]).as_posix()
            analysis = file_result["analysis"]

            imported_symbols = {}

            # Process imports
            for imported_item in analysis["imports"]:

                # Handle: from auth import login
                # Handle: from auth import login as user_login
                if "name" in imported_item:

                    module_name = imported_item["module"]
                    function_name = imported_item["name"]
                    alias_name = imported_item["alias"]

                    module_name = module_name.split(".")[-1]

                    imported_file = module_to_file.get(module_name)

                    if imported_file:

                        local_name = alias_name or function_name

                        imported_symbols[local_name] = (
                            f"{imported_file}:{function_name}"
                        )

                # Handle: import auth
                # Handle: import auth as authentication
                else:

                    module_name = imported_item["module"]
                    alias_name = imported_item["alias"]

                    local_name = alias_name or module_name.split(".")[-1]
                    module_name = module_name.split(".")[-1]

                    imported_file = module_to_file.get(module_name)

                    if imported_file:
                        imported_symbols[local_name] = imported_file

            # Resolve function calls
            for function in analysis["functions"]:

                caller_id = f"{file_path}:{function['name']}"

                for called_function in function["calls"]:

                    called_id = imported_symbols.get(called_function)

                    # Handle module-qualified calls:
                    # auth.login() or authentication.login()
                    if called_id is None and "." in called_function:

                        module_name, function_name = called_function.rsplit(".", 1)

                        imported_file = imported_symbols.get(module_name)

                        if imported_file:
                            called_id = f"{imported_file}:{function_name}"

                    # Fallback: Resolve using the symbol table
                    if called_id is None:

                        matching_symbols = symbol_table.find_symbols(
                            called_function
                        )

                        if len(matching_symbols) != 1:
                            continue

                        called_id = matching_symbols[0]

                    # Create dependency edge
                    if caller_id in self.graph and called_id in self.graph:

                        self.add_call_edge(
                            caller_id,
                            called_id
                        )
