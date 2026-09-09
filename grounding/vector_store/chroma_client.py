import os
import json
import chromadb
from chromadb.utils import embedding_functions

# Path where ChromaDB saves vectors locally inside data/chroma_db
CHROMA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")
)
EMBEDDING_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "embedding_config.json")
)

class OllamaEmbeddingFunction:
    def __init__(self, model_name: str, endpoint: str):
        self.model_name = model_name
        self.endpoint = endpoint.rstrip('/')
    
    def __call__(self, input: list[str]) -> list[list[float]]:
        import httpx
        embeddings = []
        for text in input:
            resp = httpx.post(f'{self.endpoint}/api/embeddings', json={'model': self.model_name, 'prompt': text}, timeout=30.0)
            resp.raise_for_status()
            embeddings.append(resp.json()['embedding'])
        return embeddings

def get_chroma_collection(collection_name: str = "setu_sops"):
    os.makedirs(CHROMA_DIR, exist_ok=True)
    # PersistentClient keeps data on disk so you don't lose it on restart
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    # Default lightweight embedding function (runs fast on Mac CPU)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    if os.path.exists(EMBEDDING_CONFIG_PATH):
        try:
            with open(EMBEDDING_CONFIG_PATH, "r") as f:
                config = json.load(f)
            if config.get("provider") == "ollama":
                emb_fn = OllamaEmbeddingFunction(
                    model_name=config.get("model_name", "llama3"),
                    endpoint=config.get("endpoint", "http://localhost:11434")
                )
        except Exception as e:
            print(f"Error loading embedding config: {e}")
            
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    return collection