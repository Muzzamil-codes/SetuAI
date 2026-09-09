from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
import os, json, shutil, glob
from grounding.vector_store.chroma_client import get_chroma_collection
from grounding.vector_store.ingest import chunk_text

router = APIRouter(prefix='/knowledge', tags=['knowledge'])

SOPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'sops'))
EMBEDDING_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'embedding_config.json'))

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class EmbeddingConfig(BaseModel):
    provider: str
    model_name: str
    endpoint: str

@router.get('/files')
def list_files():
    files = []
    if os.path.exists(SOPS_DIR):
        for f in os.listdir(SOPS_DIR):
            fp = os.path.join(SOPS_DIR, f)
            if os.path.isfile(fp):
                st = os.stat(fp)
                files.append({
                    "name": f,
                    "size": st.st_size,
                    "modified": st.st_mtime
                })
    return files

@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(SOPS_DIR, exist_ok=True)
    file_path = os.path.join(SOPS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Text extraction
    ext = os.path.splitext(file.filename)[1].lower()
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
            
    # Chunk and insert
    chunks = chunk_text(text)
    if chunks:
        collection = get_chroma_collection()
        documents = []
        metadatas = []
        ids = []
        for idx, chunk in enumerate(chunks):
            doc_id = f"{file.filename}_chunk_{idx}"
            documents.append(chunk)
            metadatas.append({"source": file.filename, "chunk_id": idx})
            ids.append(doc_id)
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        
    return {"status": "success", "filename": file.filename, "chunks_added": len(chunks)}

@router.delete('/files/{filename}')
def delete_file(filename: str):
    file_path = os.path.join(SOPS_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    collection = get_chroma_collection()
    collection.delete(where={"source": filename})
    return {"status": "success", "message": f"Deleted {filename}"}

@router.post('/reindex')
def reindex_all():
    collection = get_chroma_collection()
    items = collection.get()
    if items and items['ids']:
        collection.delete(ids=items['ids'])
    
    from grounding.vector_store.ingest import ingest_directory
    ingest_directory(SOPS_DIR)
    
    return {"status": "success", "message": "Reindexed all files"}

@router.post('/query')
def query_knowledge(req: QueryRequest):
    try:
        from grounding.retrieval import retrieve
        chunks = retrieve(req.query, req.top_k)
        return {"results": chunks}
    except ImportError:
        collection = get_chroma_collection()
        results = collection.query(query_texts=[req.query], n_results=req.top_k)
        return {"results": results}
    
@router.get('/embedding-config')
def get_embedding_config():
    if os.path.exists(EMBEDDING_CONFIG_PATH):
        with open(EMBEDDING_CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"provider": "default", "model_name": "", "endpoint": ""}

@router.post('/embedding-config')
def set_embedding_config(config: EmbeddingConfig):
    os.makedirs(os.path.dirname(EMBEDDING_CONFIG_PATH), exist_ok=True)
    with open(EMBEDDING_CONFIG_PATH, "w") as f:
        json.dump(config.model_dump(), f, indent=4)
    return {"status": "success"}
