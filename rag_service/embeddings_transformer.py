import os
from typing import List, Dict

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None  # Lazy import; requirements should be installed

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except Exception:
    RecursiveCharacterTextSplitter = None

try:
    import chromadb
    from chromadb.config import Settings
except Exception:
    chromadb = None
    Settings = None

MODEL_NAME = os.environ.get("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")


def _ensure_dependencies():
    if SentenceTransformer is None or RecursiveCharacterTextSplitter is None or chromadb is None:
        raise RuntimeError(
            "Missing runtime dependencies for embeddings_transformer. "
            "Install requirements from rag_service/requirements.txt (sentence-transformers, chromadb, langchain)."
        )


def setup_vectorstore(documents: List[str], collection_name: str = "aiastro") -> object:
    """
    Chunk documents, compute embeddings with SentenceTransformer,
    and persist them into a local Chroma collection.

    Args:
        documents: list of raw document strings
        collection_name: name of the chroma collection to create/append to

    Returns:
        Chroma collection object
    """
    _ensure_dependencies()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    # langchain's splitter may expect Document objects; ensure we create chunk strings
    chunks = splitter.create_documents(documents) if hasattr(splitter, "create_documents") else [d for d in documents]

    model = SentenceTransformer(MODEL_NAME)

    texts = [getattr(c, "page_content", c) for c in chunks]
    embeddings = [model.encode(t).tolist() for t in texts]
    metadatas = [getattr(c, "metadata", {}) or {"source": f"chunk_{i}"} for i, c in enumerate(chunks)]
    ids = [f"{collection_name}_{i}" for i in range(len(texts))]

    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=PERSIST_DIR))
    collection = client.get_or_create_collection(name=collection_name)

    # Add embeddings (if ids already exist, Chromadb will error — caller can remove or use new collection)
    collection.add(documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
    client.persist()
    return collection


def retrieve(query: str, collection_name: str = "aiastro", k: int = 3) -> List[Dict]:
    """
    Embed the query with the same model and return top-k results as list of dicts:
    [{ 'id': ..., 'document': ..., 'metadata': ..., 'distance': ... }, ...]
    """
    _ensure_dependencies()

    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=PERSIST_DIR))
    collection = client.get_or_create_collection(name=collection_name)
    model = SentenceTransformer(MODEL_NAME)
    q_emb = model.encode(query).tolist()

    results = collection.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas", "distances", "ids"])
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    return [
        {"id": ids[i], "document": docs[i], "metadata": metas[i], "distance": dists[i]}
        for i in range(len(docs))
    ]


if __name__ == "__main__":
    # Quick demo convenience if run directly
    sample_docs = [
        "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
        "RAG stands for Retrieval-Augmented Generation.",
        "Astrology: basic chart interpretation guidelines for Sun, Moon, Rising."
    ]
    try:
        setup_vectorstore(sample_docs, collection_name="aiastro_demo")
        print("Chroma DB populated (aiastro_demo).")
    except Exception as e:
        print("Failed to populate Chroma DB:", e)

