import chromadb
import os
try:
    from app.config import settings
except ModuleNotFoundError:
    from backend.app.config import settings


class ChromaDB:
    client = None

chroma = ChromaDB()

def connect_to_chroma():
    try:
        # Try connecting to HTTP client (Docker)
        chroma.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        # Verify connection
        chroma.client.heartbeat()
    except Exception:
        # Fallback to local persistent storage
        db_path = os.path.join(os.getcwd(), "chroma_data")
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        chroma.client = chromadb.PersistentClient(path=db_path)

def get_chroma_client():
    return chroma.client
