
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import re
import uuid

from bson import ObjectId
from pypdf import PdfReader

from app.config import (
    ALLOWED_EXTENSIONS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    MAX_UPLOAD_MB,
)
from app.db.mongo import chunks_collection, documents_collection


class DocumentProcessingError(Exception):
    """Raised when a document cannot be processed."""


def extract_text(filename: str, content: bytes) -> str:
    """Extract readable text from a PDF or TXT file."""
    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentProcessingError(
                "The TXT file must use UTF-8 encoding."
            ) from exc

    elif extension == ".pdf":
        try:
            reader = PdfReader(BytesIO(content))

            if reader.is_encrypted:
                raise DocumentProcessingError(
                    "Password-protected PDFs are not supported."
                )

            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")

            text = "\n".join(pages)

        except DocumentProcessingError:
            raise
        except Exception as exc:
            raise DocumentProcessingError(
                "Could not read this PDF file."
            ) from exc

    else:
        raise DocumentProcessingError(
            "Only PDF and TXT files are supported."
        )

    # Normalize whitespace without removing paragraph boundaries.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if not text:
        raise DocumentProcessingError(
            "No readable text found. Scanned PDFs may require OCR."
        )

    return text


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping character-based chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def process_and_store_document(
    filename: str,
    content: bytes,
    tenant_id: str,
    uploaded_by: str,
) -> dict:
    """Validate, extract, chunk, and store a document."""
    if not tenant_id or not tenant_id.strip():
        raise DocumentProcessingError("tenant_id is required.")

    if not uploaded_by or not uploaded_by.strip():
        raise DocumentProcessingError("uploaded_by is required.")

    safe_filename = Path(filename.replace("\\", "/")).name.strip()

    if not safe_filename or safe_filename in {".", ".."}:
        raise DocumentProcessingError("Invalid filename.")

    extension = Path(safe_filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentProcessingError(
            "Only PDF and TXT files are supported."
        )

    if not content:
        raise DocumentProcessingError("The uploaded file is empty.")

    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise DocumentProcessingError(
            f"File exceeds the {MAX_UPLOAD_MB} MB upload limit."
        )

    text = extract_text(safe_filename, content)
    chunks = split_into_chunks(text)

    if not chunks:
        raise DocumentProcessingError(
            "No document chunks could be created."
        )

    document_id = str(ObjectId())
    now = datetime.now(timezone.utc)

    document = {
        "_id": ObjectId(document_id),
        "tenant_id": tenant_id,
        "filename": safe_filename,
        "file_type": extension.lstrip("."),
        "file_size": len(content),
        "uploaded_by": uploaded_by,
        "status": "processed",
        "chunk_count": len(chunks),
        "created_at": now,
    }

    chunk_documents = [
        {
            "_id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "document_id": document_id,
            "chunk_index": index,
            "text": chunk,
            "created_at": now,
        }
        for index, chunk in enumerate(chunks)
    ]

    # Insert metadata first. If chunk storage fails, roll back metadata
    # and any chunks inserted for this document.
    documents_collection.insert_one(document)

    try:
        chunks_collection.insert_many(chunk_documents, ordered=True)
    except Exception:
        chunks_collection.delete_many(
            {"tenant_id": tenant_id, "document_id": document_id}
        )
        documents_collection.delete_one(
            {"_id": ObjectId(document_id), "tenant_id": tenant_id}
        )
        raise

    return {
        "document_id": document_id,
        "filename": safe_filename,
        "status": "processed",
        "chunk_count": len(chunks),
    }
