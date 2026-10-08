from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile

from sentinelia.config import Settings, get_settings
from sentinelia.models import QueryRequest, QueryResponse, UploadResponse
from sentinelia.providers import LLMProvider, create_provider
from sentinelia.rag import DocumentStore
from sentinelia.security import read_validated_upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    app.state.store = DocumentStore(settings.max_documents)
    app.state.provider = create_provider(settings)
    yield


app = FastAPI(title="SentinelIA Document Intelligence", version="0.1.0", lifespan=lifespan)


def get_store(request: Request) -> DocumentStore:
    return request.app.state.store


def get_provider(request: Request) -> LLMProvider:
    return request.app.state.provider


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/documents", response_model=UploadResponse, status_code=201)
async def upload_document(
    file: Annotated[UploadFile, File()],
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DocumentStore, Depends(get_store)],
) -> UploadResponse:
    filename, data = await read_validated_upload(file, settings.max_upload_bytes)
    try:
        document_id, chunks = store.add(filename, data)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return UploadResponse(document_id=document_id, filename=filename, chunks=chunks)


@app.post("/v1/query", response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DocumentStore, Depends(get_store)],
    provider: Annotated[LLMProvider, Depends(get_provider)],
) -> QueryResponse:
    sources = store.search(payload.question, settings.top_k)
    if not sources:
        return QueryResponse(
            answer="Les documents fournis ne permettent pas de répondre.",
            sources=[],
            grounded=False,
        )
    answer = await provider.answer(payload.question, sources)
    return QueryResponse(answer=answer, sources=sources, grounded=True)
