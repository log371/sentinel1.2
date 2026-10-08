import re
from pathlib import Path

from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/octet-stream",
}


def safe_filename(filename: str | None) -> str:
    name = Path(filename or "document").name
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", name)[:120]
    if not cleaned or cleaned.startswith("."):
        raise HTTPException(400, "Invalid filename")
    if Path(cleaned).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, "Only PDF, TXT and Markdown files are accepted")
    return cleaned


async def read_validated_upload(upload: UploadFile, max_bytes: int) -> tuple[str, bytes]:
    filename = safe_filename(upload.filename)
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "Unsupported media type")
    data = await upload.read(max_bytes + 1)
    await upload.close()
    if not data:
        raise HTTPException(400, "Empty upload")
    if len(data) > max_bytes:
        raise HTTPException(413, f"File exceeds the {max_bytes}-byte limit")
    if filename.lower().endswith(".pdf") and not data.startswith(b"%PDF-"):
        raise HTTPException(415, "The file extension and content do not match")
    if not filename.lower().endswith(".pdf") and b"\x00" in data:
        raise HTTPException(415, "Binary content is not accepted as text")
    return filename, data

