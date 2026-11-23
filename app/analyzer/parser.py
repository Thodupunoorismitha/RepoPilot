
import ast


class PythonCodeParser:

    def extract_calls(self, node):
        """Extract function and method calls from an AST node."""

        calls = []

        for child in ast.walk(node):

            if isinstance(child, ast.Call):

                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)

                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        calls.append(
                            f"{child.func.value.id}.{child.func.attr}"
                        )

        return calls

    def parse(self, source_code: str) -> dict:
        """
        Parse Python source code and extract
        functions, classes, imports, and line numbers.
        """

        tree = ast.parse(source_code)

        result = {
            "functions": [],
            "classes": [],
            "imports": [],
        }

        for node in tree.body:

            # Extract top-level functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                result["functions"].append({
                    "name": node.name,
                    "parameters": [arg.arg for arg in node.args.args],
                    "calls": self.extract_calls(node),
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                })

            # Extract classes and their methods
            elif isinstance(node, ast.ClassDef):

                methods = []

                for item in node.body:

                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):

                        methods.append({
                            "name": item.name,
                            "parameters": [arg.arg for arg in item.args.args],
                            "calls": self.extract_calls(item),
                            "start_line": item.lineno,
                            "end_line": item.end_lineno,
                        })

                result["classes"].append({
                    "name": node.name,
                    "bases": [
                        base.id for base in node.bases
                        if isinstance(base, ast.Name)
                    ],
                    "methods": methods,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                })

            # Extract regular imports           
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append({
                        "module": alias.name,
                        "alias": alias.asname
                    })

            # Extract from-import statements           
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                for alias in node.names:
                    result["imports"].append({
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname
                    })

        result["functions"].sort(key=lambda x: x["start_line"])
        result["classes"].sort(key=lambda x: x["start_line"])

        return result
