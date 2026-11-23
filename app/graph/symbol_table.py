
from pathlib import Path


class SymbolTable:

    def __init__(self):
        # Store function names and their definitions
        self.symbols = {}

    def add_symbol(self, function_name, node_id):

        if function_name not in self.symbols:
            self.symbols[function_name] = []

        self.symbols[function_name].append(node_id)

    def find_symbols(self, function_name):

        return self.symbols.get(function_name, [])


    def build_from_scan_results(self, scan_results):

        """
        Build the symbol table from repository scanner results.
        """

        for file_result in scan_results:

            # Ignore files that could not be parsed
            if file_result["status"] != "success":
                continue

            file_path = Path(file_result["file_path"]).as_posix()

            functions = file_result["analysis"]["functions"]

            for function in functions:

                function_name = function["name"]

                node_id = f"{file_path}:{function_name}"

                self.add_symbol(function_name, node_id)
