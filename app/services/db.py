import chromadb
from sentence_transformers import SentenceTransformer
from app.config import settings

db_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
collection = db_client.get_or_create_collection(name="filings")

embed_model = SentenceTransformer(settings.EMBEDDING_MODEL)

def get_collection():
    return collection

def get_embed_model():
    return embed_model
