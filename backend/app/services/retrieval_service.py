import re
from typing import Any

from app.db.mongo import db


# Common words that usually do not help identify relevant passages.
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
    """
    Retrieve relevant document chunks for a question.

    Expected MongoDB fields:
        document_id
        tenant_id
        chunk_index
        text

    Returns chunks sorted by keyword relevance.
    """

    # Validate input.
    if not question or not question.strip():
        return []

    if not document_ids or not tenant_id:
        return []

    if top_k < 1:
        return []

    query_words = set(tokenize(question))

    if not query_words:
        return []

    # Restrict the search to the selected documents
    # belonging to the specified tenant.
    collection = db["document_chunks"]

    cursor = collection.find({
        "tenant_id": tenant_id,
        "document_id": {"$in": document_ids},
    })

    results = []

    for chunk in cursor:
        text = chunk.get("text", "")

        if not isinstance(text, str) or not text.strip():
            continue

        chunk_words = set(tokenize(text))
        matched_words = query_words.intersection(chunk_words)

        if not matched_words:
            continue

        # Score = proportion of question keywords found
        # in the document chunk.
        score = len(matched_words) / len(query_words)

        results.append({
            "document_id": str(chunk["document_id"]),
            "chunk_index": chunk.get("chunk_index", 0),
            "text": text,
            "score": round(score, 4),
        })

    # Highest relevance first.
    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # Return at most 10 chunks; default is 4.
    return results[:min(top_k, 10)]
