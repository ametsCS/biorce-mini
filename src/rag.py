# src/rag.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import hashlib

import chromadb
from chromadb.utils import embedding_functions

DOCS_DIR = Path("data/docs")
CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "biorce_docs"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class RetrievedChunk:
    chunk_id: str  # C1, C2...
    doc_id: str  # filename stem (ej: S1)
    doc_title: str  # TITLE: ... (if exists)
    chunk_index: int  # 0,1,2...
    text: str
    distance: float


def _get_collection():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def _chunk_text(text: str, max_chars: int = 350, overlap: int = 80) -> List[str]:
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _extract_title(raw: str, fallback: str) -> str:
    for line in raw.splitlines():
        if line.strip().upper().startswith("TITLE:"):
            return line.split(":", 1)[1].strip() or fallback
    return fallback


def ingest_if_empty() -> None:
    collection = _get_collection()
    if collection.count() > 0:
        return

    txt_files = sorted(DOCS_DIR.glob("*.txt"))
    if not txt_files:
        raise RuntimeError("No docs found in data/docs. Add some .txt files first.")

    ids, documents, metadatas = [], [], []

    for f in txt_files:
        raw = f.read_text(encoding="utf-8")
        title = _extract_title(raw, fallback=f.stem)

        chunks = _chunk_text(raw)
        for idx, c in enumerate(chunks):
            h = hashlib.md5((f.name + str(idx) + c).encode("utf-8")).hexdigest()[:16]
            ids.append(f"{f.stem}_{idx}_{h}")
            documents.append(c)
            metadatas.append({"doc_id": f.stem, "title": title, "chunk_index": idx})

    collection.add(ids=ids, documents=documents, metadatas=metadatas)


def retrieve(query: str, k: int = 5) -> List[RetrievedChunk]:
    collection = _get_collection()
    res = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]

    out: List[RetrievedChunk] = []
    for rank, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
        out.append(
            RetrievedChunk(
                chunk_id=f"C{rank}",
                doc_id=str(meta.get("doc_id", meta.get("source", "unknown"))),
                doc_title=str(meta.get("title", meta.get("source", "unknown"))),
                chunk_index=int(meta.get("chunk_index", meta.get("chunk", -1))),
                text=doc,
                distance=float(dist),
            )
        )
    return out
