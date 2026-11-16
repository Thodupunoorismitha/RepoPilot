
import os
from app.analyzer.parser import PythonCodeParser


class RepositoryScanner:

    def __init__(self):
        self.parser = PythonCodeParser()

    def scan(self, repo_path: str):

        results = []

        ignored_dirs = {".venv", "__pycache__", ".git"}

        for root, dirs, files in os.walk(repo_path):

            dirs[:] = [
                directory for directory in dirs
                if directory not in ignored_dirs
            ]

            for file in files:

                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)

                # Step 1: Read the source file
                try:
                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as source_file:
                        source_code = source_file.read()

                except (OSError, UnicodeDecodeError) as error:

                    results.append({
                        "file_path": file_path,
                        "status": "error",
                        "error_type": type(error).__name__,
                        "error": str(error)
                    })

                    continue

                # Step 2: Parse the source code
                try:
                    parsed_data = self.parser.parse(source_code)

                    results.append({
                        "file_path": file_path,
                        "status": "success",
                        "analysis": parsed_data
                    })

                except SyntaxError as error:

                    results.append({
                        "file_path": file_path,
                        "status": "error",
                        "error_type": type(error).__name__,
                        "error": str(error)
                    })

        return results
