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
    sid: str  # S1, S2...
    source: str  # filename stem
    text: str  # chunk text
    distance: float  # similarity distance (lower is better)


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


def _chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> List[str]:
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


def ingest_if_empty() -> None:
    collection = _get_collection()
    if collection.count() > 0:
        return

    txt_files = sorted(DOCS_DIR.glob("*.txt"))
    if not txt_files:
        raise RuntimeError("No docs found in data/docs. Add some .txt files first.")

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for f in txt_files:
        raw = f.read_text(encoding="utf-8")
        chunks = _chunk_text(raw)

        for idx, c in enumerate(chunks):
            # ID estable por contenido
            h = hashlib.md5((f.name + str(idx) + c).encode("utf-8")).hexdigest()[:16]
            ids.append(f"{f.stem}_{idx}_{h}")
            documents.append(c)
            metadatas.append({"source": f.stem, "chunk": idx})

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
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
        out.append(
            RetrievedChunk(
                sid=f"S{i}",
                source=str(meta.get("source", "unknown")),
                text=doc,
                distance=float(dist),
            )
        )
    return out
