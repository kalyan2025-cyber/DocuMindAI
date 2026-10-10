
from app.db.mongo import (
    check_database,
    chunks_collection,
    documents_collection,
)
from app.services.document_service import process_and_store_document

assert check_database(), "MongoDB is not reachable."

result = process_and_store_document(
    filename="documind_sample.txt",
    content=(
        b"DocuMindAI is a business knowledge assistant. "
        b"It answers questions using uploaded business documents."
    ),
    tenant_id="local-test-tenant",
    uploaded_by="local-test-user",
)

print("Document storage test passed!")
print("Result:", result)

saved_document = documents_collection.find_one({
    "_id": __import__("bson").ObjectId(result["document_id"]),
    "tenant_id": "local-test-tenant",
})

saved_chunks = list(chunks_collection.find({
    "tenant_id": "local-test-tenant",
    "document_id": result["document_id"],
}).sort("chunk_index", 1))

assert saved_document is not None, "Document metadata was not saved."
assert len(saved_chunks) == result["chunk_count"], "Chunk count mismatch."

print("Saved filename:", saved_document["filename"])
print("Saved chunk count:", len(saved_chunks))
print("First chunk:", saved_chunks[0]["text"])

