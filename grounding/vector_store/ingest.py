import os
import glob
from grounding.vector_store.chroma_client import get_chroma_collection

def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
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
    files = glob.glob(os.path.join(sops_dir, "*"))
    
    documents = []
    metadatas = []
    ids = []
    
    for file_path in files:
        if os.path.isdir(file_path):
            continue
            
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        text = ""
        
        if ext in ['.txt', '.md', '.csv', '.json']:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext == '.pdf':
            try:
                import fitz
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
            except ImportError:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
        elif ext == '.docx':
            try:
                import docx
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except ImportError:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                
        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{filename}_chunk_{idx}"
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk_id": idx})
            ids.append(doc_id)
            
    if documents:
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"✅ Ingestion complete: {len(documents)} chunks from {len(files)} files stored in ChromaDB.")
    else:
        print("⚠️ No valid files found or chunks generated in", sops_dir)

if __name__ == "__main__":
    ingest_directory()