from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    repo_path: str


class AnalyzeResponse(BaseModel):
    total_files: int
    successful_files: int
    failed_files: int
    repository_id: int
    symbols_saved: int
    relationships_saved: int
    message: str