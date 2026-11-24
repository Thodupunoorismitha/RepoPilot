
from pathlib import Path


class CodeChunker:

    def create_chunks(self, scan_results):
        """
        Extract functions and classes as individual code chunks.
        """

        chunks = []

        chunk_id = 1

        for file_result in scan_results:

            if file_result["status"] != "success":
                continue

            file_path = file_result["file_path"]
            analysis = file_result["analysis"]

            # Read the original source code
            try:
                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as source_file:
                    source_lines = source_file.readlines()

            except (OSError, UnicodeDecodeError):
                continue

            # Combine functions and classes
            symbols = []

            for function in analysis["functions"]:
                symbols.append({
                    **function,
                    "type": "function"
                })

            for class_info in analysis["classes"]:
                symbols.append({
                    **class_info,
                    "type": "class"
                })

            # Extract source code for each symbol
            for symbol in symbols:

                start_line = symbol["start_line"]
                end_line = symbol["end_line"]

                content = "".join(
                    source_lines[start_line - 1:end_line]
                )

                chunks.append({
                    "chunk_id": chunk_id,
                    "file_path": file_path,
                    "symbol_name": symbol["name"],
                    "chunk_type": symbol["type"],
                    "start_line": start_line,
                    "end_line": end_line,
                    "content": content
                })

                chunk_id += 1

        return chunks
