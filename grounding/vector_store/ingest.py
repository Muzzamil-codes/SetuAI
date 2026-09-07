import os
import glob
from grounding.vector_store.chroma_client import get_chroma_collection

def chunk_text(text: str, chunk_size: int = 250) -> list[str]:
    """Splits SOP text into manageable chunks for vector search."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) <= chunk_size:
            current_chunk += " " + p if current_chunk else p
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = p
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def ingest_directory(sops_dir: str = "data/sops"):
    collection = get_chroma_collection()
    files = glob.glob(os.path.join(sops_dir, "*.txt"))
    
    documents = []
    metadatas = []
    ids = []
    
    for file_path in files:
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        chunks = chunk_text(content)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{filename}_chunk_{idx}"
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk_id": idx})
            ids.append(doc_id)
            
    if documents:
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"✅ Ingestion complete: {len(documents)} chunks from {len(files)} files stored in ChromaDB.")
    else:
        print("⚠️ No .txt files found in", sops_dir)

if __name__ == "__main__":
    ingest_directory()