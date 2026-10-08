from pydantic import BaseModel, Field


class Source(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    page: int | None = None
    excerpt: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    grounded: bool


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int

