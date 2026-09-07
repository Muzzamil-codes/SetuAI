import os
import chromadb
from chromadb.utils import embedding_functions

# Path where ChromaDB saves vectors locally inside data/chroma_db
CHROMA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")
)

def get_chroma_collection(collection_name: str = "setu_sops"):
    os.makedirs(CHROMA_DIR, exist_ok=True)
    # PersistentClient keeps data on disk so you don't lose it on restart
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    # Default lightweight embedding function (runs fast on Mac CPU)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    return collection