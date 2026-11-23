from pathlib import Path

from app.analyzer.scanner import RepositoryScanner
from app.graph.symbol_table import SymbolTable
from app.graph.dependency_graph import DependencyGraphBuilder


class RepositoryAnalysisService:

    def __init__(self):
        self.scanner = RepositoryScanner()

    def analyze_repository(self, repo_path: str):

        path = Path(repo_path)

        # Step 1: Validate repository path
        if not path.exists():
            raise FileNotFoundError("Repository path does not exist")

        if not path.is_dir():
            raise NotADirectoryError("Provided path is not a directory")

        # Step 2: Scan repository
        scan_results = self.scanner.scan(str(path))

        # Step 3: Build symbol table
        symbol_table = SymbolTable()
        symbol_table.build_from_scan_results(scan_results)

        # Step 4: Build dependency graph
        graph_builder = DependencyGraphBuilder()

        for file_result in scan_results:

            if file_result["status"] != "success":
                continue

            file_path = file_result["file_path"]
            functions = file_result["analysis"]["functions"]

            graph_builder.add_functions_from_file(
                file_path,
                functions
            )

        graph_builder.build_cross_file_edges(
            scan_results,
            symbol_table
        )

        # Step 5: Calculate summary
        total_files = len(scan_results)

        successful_files = sum(
            1 for result in scan_results
            if result["status"] == "success"
        )

        failed_files = total_files - successful_files

        return {
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "symbol_table": symbol_table,
            "graph_builder": graph_builder,
            "scan_results": scan_results
        }