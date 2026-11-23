from fastapi import FastAPI, HTTPException
import networkx as nx
from app.analyzer.service import RepositoryAnalysisService
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse


app = FastAPI(
    title="RepoPilot API",
    description="AI-powered codebase intelligence platform",
    version="0.1.0",
)


analysis_service = RepositoryAnalysisService()
app.state.analysis_result = None


@app.get("/health")
def health_check():
    """Return the operational status of the API."""
    return {
        "status": "ok",
        "service": "repopilot-api",
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_repository(request: AnalyzeRequest):
    """Analyze a Python repository."""

    try:
        result = analysis_service.analyze_repository(
            request.repo_path
        )
        app.state.analysis_result = result

        return {
            "total_files": result["total_files"],
            "successful_files": result["successful_files"],
            "failed_files": result["failed_files"],
            "message": "Repository analysis completed"
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except NotADirectoryError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@app.get("/symbols")
def search_symbols(name: str):

    # Check whether a repository has been analyzed
    analysis_result = app.state.analysis_result

    if analysis_result is None:
        raise HTTPException(
            status_code=400,
            detail="Analyze a repository first"
        )

    # Search for matching functions
    symbol_table = analysis_result["symbol_table"]

    matching_symbols = symbol_table.find_symbols(name)

    # Convert matching symbol IDs into response details
    matches = []

    for symbol_id in matching_symbols:

        file_path, function_name = symbol_id.rsplit(":", 1)

        scan_results = analysis_result["scan_results"]

        for file_result in scan_results:

            if file_result["status"] != "success":
                continue

            if file_result["file_path"].replace("\\", "/") != file_path:
                continue

            for function in file_result["analysis"]["functions"]:

                if function["name"] == function_name:

                    matches.append({
                        "file_path": file_path,
                        "start_line": function["start_line"],
                        "end_line": function["end_line"]
                    })

    return {
        "name": name,
        "matches": matches
    }

@app.get("/callers/{name}")
def find_callers(name: str):

    # Check whether a repository has been analyzed
    analysis_result = app.state.analysis_result

    if analysis_result is None:
        raise HTTPException(
            status_code=400,
            detail="Analyze a repository first"
        )

    graph = analysis_result["graph_builder"].graph
    symbol_table = analysis_result["symbol_table"]

    # Find matching function IDs
    matching_symbols = symbol_table.find_symbols(name)

    if not matching_symbols:
        raise HTTPException(
            status_code=404,
            detail=f"Function '{name}' not found"
        )

    results = []

    for symbol_id in matching_symbols:

        # Find all direct callers
        caller_ids = list(graph.predecessors(symbol_id))

        callers = []

        for caller_id in caller_ids:

            caller_details = graph.nodes[caller_id]

            callers.append({
                "name": caller_details["name"],
                "file_path": caller_details["file_path"],
                "start_line": caller_details["start_line"]
            })

        results.append({
            "file_path": graph.nodes[symbol_id]["file_path"],
            "callers": callers
        })

    return {
        "function": name,
        "results": results
    }

@app.get("/dependencies/{name}")
def find_dependencies(name: str):

    # Check whether a repository has been analyzed
    analysis_result = app.state.analysis_result

    if analysis_result is None:
        raise HTTPException(
            status_code=400,
            detail="Analyze a repository first"
        )

    graph = analysis_result["graph_builder"].graph
    symbol_table = analysis_result["symbol_table"]

    # Find matching function IDs
    matching_symbols = symbol_table.find_symbols(name)

    if not matching_symbols:
        raise HTTPException(
            status_code=404,
            detail=f"Function '{name}' not found"
        )

    results = []

    for symbol_id in matching_symbols:

        # Find functions called by this function
        dependency_ids = list(graph.successors(symbol_id))

        dependencies = []

        for dependency_id in dependency_ids:

            dependency_details = graph.nodes[dependency_id]

            dependencies.append({
                "name": dependency_details["name"],
                "file_path": dependency_details["file_path"],
                "start_line": dependency_details["start_line"]
            })

        results.append({
            "file_path": graph.nodes[symbol_id]["file_path"],
            "dependencies": dependencies
        })

    return {
        "function": name,
        "results": results
    }

@app.get("/impact/{name}")
def analyze_impact(name: str):

    # Check whether a repository has been analyzed
    analysis_result = app.state.analysis_result

    if analysis_result is None:
        raise HTTPException(
            status_code=400,
            detail="Analyze a repository first"
        )

    graph = analysis_result["graph_builder"].graph
    symbol_table = analysis_result["symbol_table"]

    # Find matching function IDs
    matching_symbols = symbol_table.find_symbols(name)

    if not matching_symbols:
        raise HTTPException(
            status_code=404,
            detail=f"Function '{name}' not found"
        )

    results = []

    for symbol_id in matching_symbols:

        # Find all direct and indirect callers
        affected_ids = nx.ancestors(graph, symbol_id)

        affected_functions = []

        for affected_id in affected_ids:

            function_details = graph.nodes[affected_id]

            affected_functions.append({
                "name": function_details["name"],
                "file_path": function_details["file_path"],
                "start_line": function_details["start_line"]
            })

        results.append({
            "file_path": graph.nodes[symbol_id]["file_path"],
            "affected_functions": affected_functions
        })

    return {
        "function": name,
        "results": results
    }