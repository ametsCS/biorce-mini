from src.rag import ingest_if_empty

if __name__ == "__main__":
    ingest_if_empty()
    print("✅ RAG ingest OK (or already indexed).")
