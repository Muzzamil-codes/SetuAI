import re
from grounding.vector_store.chroma_client import get_chroma_collection

def retrieve(query: str, top_k: int = 5) -> dict:
    """Queries ChromaDB and returns top-k matching SOP chunks (API Contract 3.6)."""
    collection = get_chroma_collection()
    results = collection.query(query_texts=[query], n_results=top_k)
    
    chunks = []
    if results and results.get("documents") and len(results["documents"]) > 0:
        docs = results["documents"][0]
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
        
        for doc, meta, dist in zip(docs, metadatas, distances):
            score = round(max(0.0, 1.0 - (dist if dist is not None else 0.5)), 3)
            chunks.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "score": score
            })
            
    return {"chunks": chunks}

def verify_claim(claim: str, chunks: list[dict]) -> dict:
    """Verifies if an AI claim is supported by retrieved evidence (API Contract 3.7)."""
    if not chunks:
        return {"supported": False, "confidence": 0.0}

    def tokenize(s: str) -> set[str]:
        return set(re.findall(r"\b\w+\b", s.lower()))

    claim_tokens = tokenize(claim)
    stopwords = {"is", "the", "a", "an", "and", "or", "in", "of", "to", "for", "per", "at", "by", "with"}
    key_claim_tokens = claim_tokens - stopwords

    if not key_claim_tokens:
        return {"supported": False, "confidence": 0.0}

    best_match_ratio = 0.0
    for chunk in chunks:
        chunk_tokens = tokenize(chunk.get("text", ""))
        matched = key_claim_tokens.intersection(chunk_tokens)
        ratio = len(matched) / len(key_claim_tokens)
        if ratio > best_match_ratio:
            best_match_ratio = ratio

    supported = best_match_ratio >= 0.5
    return {"supported": supported, "confidence": round(best_match_ratio, 2)}