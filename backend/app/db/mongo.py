
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

from app.config import MONGODB_DATABASE, MONGODB_URI

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000,
)

db = client[MONGODB_DATABASE]

users_collection = db["users"]
documents_collection = db["documents"]
chunks_collection = db["document_chunks"]
sessions_collection = db["chat_sessions"]
messages_collection = db["chat_messages"]
leads_collection = db["leads"]


def check_database() -> bool:
    """Check whether MongoDB is reachable."""
    try:
        client.admin.command("ping")
        return True
    except PyMongoError:
        return False


def create_indexes() -> None:
    """Create indexes used by the application."""
    users_collection.create_index(
        [("firebase_uid", ASCENDING)],
        unique=True,
        sparse=True,
    )

    documents_collection.create_index(
        [("tenant_id", ASCENDING), ("created_at", DESCENDING)]
    )

    chunks_collection.create_index(
        [
            ("tenant_id", ASCENDING),
            ("document_id", ASCENDING),
            ("chunk_index", ASCENDING),
        ],
        unique=True,
    )

    sessions_collection.create_index(
        [
            ("tenant_id", ASCENDING),
            ("user_id", ASCENDING),
            ("created_at", DESCENDING),
        ]
    )

    messages_collection.create_index(
        [
            ("tenant_id", ASCENDING),
            ("session_id", ASCENDING),
            ("created_at", ASCENDING),
        ]
    )

    leads_collection.create_index(
        [("tenant_id", ASCENDING), ("created_at", DESCENDING)]
    )
