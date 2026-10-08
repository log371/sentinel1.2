import io
import math
import re
from collections import Counter
from dataclasses import dataclass
from uuid import uuid4

from pypdf import PdfReader

from sentinelia.models import Source

TOKEN_RE = re.compile(r"[\wÀ-ÿ]{2,}", re.UNICODE)


@dataclass
class Chunk:
    document_id: str
    filename: str
    chunk_id: str
    text: str
    page: int | None


def _tokens(text: str) -> Counter[str]:
    return Counter(token.lower() for token in TOKEN_RE.findall(text))


def _similarity(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    denominator = math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
    return 0.0 if denominator == 0 else sum(v * b.get(k, 0) for k, v in a.items()) / denominator


def _split(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    chunks, start = [], 0
    while start < len(normalized):
        end = min(start + size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            end = boundary if boundary > start else end
        chunks.append(normalized[start:end])
        if end == len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


class DocumentStore:
    def __init__(self, max_documents: int = 100) -> None:
        self.max_documents = max_documents
        self.chunks: list[Chunk] = []
        self.document_ids: set[str] = set()

    def add(self, filename: str, data: bytes) -> tuple[str, int]:
        if len(self.document_ids) >= self.max_documents:
            raise ValueError("Document capacity reached")
        document_id = str(uuid4())
        pages: list[tuple[int | None, str]]
        if filename.lower().endswith(".pdf"):
            pdf_pages = PdfReader(io.BytesIO(data)).pages
            pages = [
                (number, page.extract_text() or "")
                for number, page in enumerate(pdf_pages, 1)
            ]
        else:
            pages = [(None, data.decode("utf-8"))]
        created = 0
        for page, text in pages:
            for index, part in enumerate(_split(text), 1):
                chunk_id = f"{document_id}:{page or 0}:{index}"
                self.chunks.append(Chunk(document_id, filename, chunk_id, part, page))
                created += 1
        if not created:
            raise ValueError("No extractable text found")
        self.document_ids.add(document_id)
        return document_id, created

    def search(self, question: str, top_k: int) -> list[Source]:
        ranked = sorted(
            ((chunk, _similarity(question, chunk.text)) for chunk in self.chunks),
            key=lambda item: item[1],
            reverse=True,
        )
        return [
            Source(
                document_id=c.document_id,
                filename=c.filename,
                chunk_id=c.chunk_id,
                page=c.page,
                excerpt=c.text[:500],
                score=round(score, 4),
            )
            for c, score in ranked[:top_k]
            if score > 0
        ]
