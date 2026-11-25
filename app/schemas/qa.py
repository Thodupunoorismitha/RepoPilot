
from pydantic import BaseModel


class AskRequest(BaseModel):
    repository_id: int
    question: str
    top_k: int = 5


class SourceReference(BaseModel):
    file_path: str
    symbol_name: str
    start_line: int
    end_line: int
    similarity: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceReference]
