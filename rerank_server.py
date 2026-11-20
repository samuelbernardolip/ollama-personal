#!/usr/bin/env python3
"""
TEI-Compatible CPU Cross-Encoder Reranker Server
Optimized for VS Code Continue Extension RAG Pipeline
Runs 100% on CPU (0 MB VRAM)
"""

import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import CrossEncoder

MODEL_NAME = os.getenv("MODEL_NAME", "BAAI/bge-reranker-base")
DEVICE = os.getenv("DEVICE", "cpu")
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")

app = FastAPI(
    title="Continue Local CPU Reranker",
    description="TEI-compatible local cross-encoder rerank API for VS Code Continue RAG",
    version="1.0.0",
)

# Initialize CrossEncoder model on CPU
print(f"[*] Loading CrossEncoder model '{MODEL_NAME}' on {DEVICE}...")
try:
    model = CrossEncoder(MODEL_NAME, device=DEVICE)
    # Warmup inference pass to compile execution graph
    _ = model.predict([["Warmup query", "Warmup passage"]])
    print(f"[+] Model '{MODEL_NAME}' loaded successfully. Ready for RAG requests.")
except Exception as e:
    print(f"[!] Critical error loading model '{MODEL_NAME}': {e}", file=sys.stderr)
    model = None

class RerankRequest(BaseModel):
    query: str
    texts: Optional[List[str]] = Field(default=None, description="Candidate snippets (TEI format)")
    documents: Optional[List[str]] = Field(default=None, description="Candidate snippets (Cohere format)")

@app.get("/health")
def health():
    """Health check endpoint matching Hugging Face TEI specification."""
    if model is None:
        raise HTTPException(status_code=503, detail="Reranker model failed to initialize")
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "device": DEVICE,
        "threads": os.getenv("OMP_NUM_THREADS", "auto")
    }

@app.post("/rerank")
def rerank(req: RerankRequest):
    """
    Reranks candidate snippets against the query.
    Returns scored results sorted or indexed as expected by Continue's huggingface-tei provider.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Reranker model not available")
    
    candidates = req.texts if req.texts is not None else req.documents
    if not candidates:
        return []

    # Construct query-document pairs
    pairs = [[req.query, doc] for doc in candidates]
    
    # Compute cross-encoder relevance scores
    scores = model.predict(pairs).tolist()
    
    # Return formatted objects with original index and relevance score
    return [{"index": i, "score": float(s)} for i, s in enumerate(scores)]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
