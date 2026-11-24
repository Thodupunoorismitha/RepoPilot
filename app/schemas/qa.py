from pydantic import BaseModel

class QARequest(BaseModel):
    repository_id: int
    question: str
    top_k: int = 5

class QASource(BaseModel):
    file_path: str
    symbol_name: str
    start_line: int
    end_line: int
    similarity: float

class QAResponse(BaseModel):
    question: str
    answer: str
    sources: list[QASource]