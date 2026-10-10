
import re
from typing import Any

from bson import ObjectId

from app.db.mongo import db


STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "what", "when", "where", "who", "how", "why",
    "do", "does", "did", "can", "could", "i", "we",
    "you", "they", "it", "to", "of", "in", "on",
    "for", "and", "or", "my", "our", "your", "have",
    "has", "had", "be", "with", "about", "please",
}


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase keywords."""
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def retrieve_chunks(
    question: str,
    document_ids: list[str],
    tenant_id: str,
    top_k: int = 4,
) -> list[dict[str, Any]]:
    """Retrieve relevant chunks with document filenames."""

    if not question or not question.strip():
        return []

    if not document_ids or not tenant_id:
        return []

    if top_k < 1:
        return []

    query_words = set(tokenize(question))
    if not query_words:
        return []

    chunks_collection = db["document_chunks"]
    documents_collection = db["documents"]

    # Only search selected documents belonging to this tenant.
    cursor = chunks_collection.find({
        "tenant_id": tenant_id,
        "document_id": {"$in": document_ids},
    })

    # Fetch metadata for the selected documents in one query.
    document_metadata = {}

    metadata_cursor = documents_collection.find({
        "_id": {
            "$in": [
                ObjectId(document_id)
                for document_id in document_ids
                if ObjectId.is_valid(document_id)
            ]
        },
        "tenant_id": tenant_id,
    })

    for document in metadata_cursor:
        document_metadata[str(document["_id"])] = document

    results = []

    for chunk in cursor:
        text = chunk.get("text", "")

        if not isinstance(text, str) or not text.strip():
            continue

        document_id = str(chunk.get("document_id", ""))
        document = document_metadata.get(document_id)

        # Ignore orphaned chunks or documents outside this tenant.
        if not document:
            continue

        chunk_words = set(tokenize(text))
        matched_words = query_words.intersection(chunk_words)

        if not matched_words:
            continue

        score = len(matched_words) / len(query_words)

        results.append({
            "document_id": document_id,
            "filename": document.get(
                "filename",
                "Unknown document",
            ),
            "chunk_index": chunk.get("chunk_index", 0),
            "text": text,
            "score": round(score, 4),
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:min(top_k, 10)]
