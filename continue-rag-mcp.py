#!/usr/bin/env python3
"""
continue-rag-mcp - Local Vector Database & Python Reranker MCP Server
Implements Custom Code RAG per Continue Docs (https://docs.continue.dev/guides/custom-code-rag)
Connects to local LanceDB index, vectors via ollama-embed-cpu, and reranks via Python rerank-server.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error

HOME = os.path.expanduser("~")
LANCEDB_DIR = os.getenv("LANCEDB_DIR", os.path.join(HOME, ".continue", "index", "lancedb"))
EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://localhost:11435/api/embeddings")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
RERANK_URL = os.getenv("RERANK_URL", "http://localhost:8080/rerank")

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def get_query_embedding(query):
    """Generate query vector embedding via Ollama CPU instance (port 11435)."""
    payload = json.dumps({"model": EMBED_MODEL, "prompt": query}).encode("utf-8")
    req = urllib.request.Request(
        EMBED_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("embedding", [])

def rerank_candidate_chunks(query, candidates, top_k):
    """Rerank candidate snippets using the local Python Cross-Encoder on port 8080."""
    if not candidates:
        return []
    texts = [c["text"] for c in candidates]
    payload = json.dumps({"query": query, "texts": texts}).encode("utf-8")
    req = urllib.request.Request(
        RERANK_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            scores = json.loads(resp.read().decode("utf-8"))
            for item in scores:
                idx = item.get("index", 0)
                if idx < len(candidates):
                    candidates[idx]["score"] = item.get("score", 0.0)
            candidates.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            return candidates[:top_k]
    except Exception:
        for c in candidates:
            c["score"] = "unranked (reranker offline)"
        return candidates[:top_k]

def search_lancedb(query, limit=3, table_name="code_chunks"):
    """Query LanceDB vector store and pass candidates to the local reranker."""
    try:
        import lancedb
        if not os.path.exists(LANCEDB_DIR):
            return [{
                "filename": "NOTE",
                "text": f"LanceDB directory '{LANCEDB_DIR}' not yet indexed. Run codebase indexing in Continue first.",
                "score": 0.0
            }]
        db = lancedb.connect(LANCEDB_DIR)
        table_names = db.table_names()
        if not table_names:
            return [{
                "filename": "NOTE",
                "text": f"No tables found in LanceDB database at '{LANCEDB_DIR}'. Index repository files first.",
                "score": 0.0
            }]
        target_table = table_name if table_name in table_names else table_names[0]
        table = db.open_table(target_table)
        
        retrieve_pool = max(limit * 4, 15)
        raw_results = table.search(query).limit(retrieve_pool).to_list()
        
        candidates = []
        for r in raw_results:
            candidates.append({
                "filename": r.get("filename", "unknown"),
                "text": r.get("text", "")
            })
        
        return rerank_candidate_chunks(query, candidates, top_k=limit)
    except ImportError:
        return [{
            "filename": "DEPENDENCY_NOTICE",
            "text": "Python 'lancedb' package is not installed. Install via: pip install lancedb",
            "score": 0.0
        }]
    except Exception as e:
        return [{
            "filename": "ERROR",
            "text": f"Error querying vector database: {str(e)}",
            "score": 0.0
        }]

def get_file_chunks(filename, table_name="code_chunks"):
    """Fetch all indexed chunks belonging to a specific file path."""
    try:
        import lancedb
        if not os.path.exists(LANCEDB_DIR):
            return f"LanceDB directory '{LANCEDB_DIR}' not found."
        db = lancedb.connect(LANCEDB_DIR)
        table_names = db.table_names()
        if not table_names:
            return "No indexed tables available in LanceDB."
        target_table = table_name if table_name in table_names else table_names[0]
        table = db.open_table(target_table)
        
        results = table.where(f"filename = '{filename}'").to_list()
        if not results:
            base = os.path.basename(filename)
            results = [r for r in table.to_list() if base in r.get("filename", "")]
        
        if not results:
            return f"No indexed chunks found for file: {filename}"
        
        chunks = [r.get("text", "") for r in results]
        return "\n\n---\n\n".join(chunks)
    except ImportError:
        return "Python 'lancedb' package is not installed. Install via: pip install lancedb"
    except Exception as e:
        return f"Error retrieving file context: {str(e)}"

def list_tables():
    """List all indexed repository tables in LanceDB."""
    try:
        import lancedb
        if not os.path.exists(LANCEDB_DIR):
            return ["No LanceDB directory at: " + LANCEDB_DIR]
        db = lancedb.connect(LANCEDB_DIR)
        return db.table_names() or ["(database exists but has 0 tables)"]
    except ImportError:
        return ["(lancedb not installed)"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def handle_jsonrpc(req):
    req_id = req.get("id")
    method = req.get("method")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "continue-rag-mcp", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "search_codebase",
                        "description": "Search the local codebase vector database (LanceDB) with cross-encoder CPU reranking (bge-reranker-base on port 8080).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Semantic code search query, function description, or technical error"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of top reranked chunks to return (default: 3, matches Continue nFinal)",
                                    "default": 3
                                },
                                "table_name": {
                                    "type": "string",
                                    "description": "Optional LanceDB collection/table name (default: 'code_chunks')",
                                    "default": "code_chunks"
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "get_file_context",
                        "description": "Retrieve all indexed code chunks for a specific file path from the local vector database.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "Relative or absolute file path to look up in the vector index"
                                },
                                "table_name": {
                                    "type": "string",
                                    "description": "Optional LanceDB collection/table name",
                                    "default": "code_chunks"
                                }
                            },
                            "required": ["filename"]
                        }
                    },
                    {
                        "name": "list_indexed_repositories",
                        "description": "List all indexed repository tables available in the local LanceDB vector store.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "search_codebase":
            query = args.get("query", "")
            limit = int(args.get("limit", 3))
            table_name = args.get("table_name", "code_chunks")
            results = search_lancedb(query, limit=limit, table_name=table_name)
            
            content_blocks = []
            for r in results:
                score_str = f" [Score: {r['score']:.4f}]" if isinstance(r.get("score"), float) else ""
                content_blocks.append({
                    "type": "text",
                    "text": f"=== File: {r['filename']}{score_str} ===\n{r['text']}"
                })
            
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": content_blocks, "isError": False}
            }
        elif tool_name == "get_file_context":
            filename = args.get("filename", "")
            table_name = args.get("table_name", "code_chunks")
            text = get_file_chunks(filename, table_name=table_name)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"=== Context for {filename} ===\n{text}"}],
                    "isError": False
                }
            }
        elif tool_name == "list_indexed_repositories":
            tables = list_tables()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": "Indexed LanceDB Tables:\n- " + "\n- ".join(tables)}],
                    "isError": False
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                    "isError": True
                }
            }

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" not in req:
            continue
        resp = handle_jsonrpc(req)
        send(resp)

if __name__ == "__main__":
    main()
