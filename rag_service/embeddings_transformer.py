import os
import uuid
from typing import List, Dict, Any, Optional

MODEL_NAME = os.environ.get("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
DEFAULT_COLLECTION = os.environ.get("CHROMA_COLLECTION", "aiastro")
EMBEDDING_BACKEND = os.environ.get("EMBEDDING_BACKEND", "sentence_transformers")


def _import_optional(name: str):
    try:
        module = __import__(name)
        return module
    except Exception:
        return None


# Lazy imports
_sentence_transformers = _import_optional("sentence_transformers")
_langchain_text_splitter = _import_optional("langchain.text_splitter")
_langchain_openai_embeddings = _import_optional("langchain_openai")
_chromadb = _import_optional("chromadb")
_chromadb_config = _import_optional("chromadb.config")


def _ensure_dependencies(backend: Optional[str] = None) -> None:
    """
    Ensure runtime dependencies are available for the chosen backend.
    """
    backend = backend or EMBEDDING_BACKEND
    missing = []

    if _langchain_text_splitter is None:
        missing.append("langchain (text_splitter)")

    if _chromadb is None or _chromadb_config is None:
        missing.append("chromadb")

    if backend == "sentence_transformers" and _sentence_transformers is None:
        missing.append("sentence-transformers")
    if backend in ("openai", "langchain_openai") and _langchain_openai_embeddings is None:
        # note: package name may vary; langchain-openai provides OpenAIEmbeddings
        missing.append("langchain-openai (or a compatible OpenAI embeddings provider)")

    if missing:
        raise RuntimeError(
            "Missing runtime dependencies: " + ", ".join(missing) + ".\n"
            "Install rag_service/requirements.txt or add the required packages."
        )


def _get_texts_from_documents(documents: List[Any]) -> List[str]:
    """Normalize input documents into list of plain text strings.
    Accepts list of strings or objects with a `page_content` attribute.
    """
    texts: List[str] = []
    for d in documents:
        if isinstance(d, str):
            texts.append(d)
        else:
            # try common attribute names
            txt = getattr(d, "page_content", None) or getattr(d, "content", None) or str(d)
            texts.append(txt)
    return texts


def list_collections(persist_dir: Optional[str] = None) -> List[str]:
    """Return a list of Chromadb collection names in the persist directory (best-effort)."""
    persist_dir = persist_dir or PERSIST_DIR
    _ensure_dependencies()
    client = _chromadb.Client(_chromadb_config.Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir))
    try:
        return [c.name for c in client.list_collections()]
    except Exception:
        # Some chroma versions return different shapes; be permissive
        try:
            return client.list_collections()
        except Exception:
            return []


def delete_collection(collection_name: str, persist_dir: Optional[str] = None) -> bool:
    """Delete a chroma collection if it exists. Returns True if deleted or not present."""
    persist_dir = persist_dir or PERSIST_DIR
    _ensure_dependencies()
    client = _chromadb.Client(_chromadb_config.Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir))
    try:
        client.delete_collection(name=collection_name)
        client.persist()
        return True
    except Exception:
        # fallback: try to get collection and purge
        try:
            coll = client.get_or_create_collection(name=collection_name)
            coll.delete()
            client.persist()
            return True
        except Exception:
            return False


def setup_vectorstore(
    documents: List[Any],
    collection_name: str = DEFAULT_COLLECTION,
    chunk_size: int = 300,
    chunk_overlap: int = 50,
    persist: bool = True,
    overwrite: bool = False,
    backend: Optional[str] = None,
) -> Any:
    """
    Normalize documents, chunk, embed, and upsert into a Chroma collection.

    Args:
        documents: list of strings or Document-like objects
        collection_name: chroma collection name
        chunk_size, chunk_overlap: splitting params
        persist: whether to persist the Chroma client to disk
        overwrite: if True, delete existing collection before creating
        backend: 'sentence_transformers' (default) or 'openai'

    Returns:
        chroma collection object
    """
    backend = backend or EMBEDDING_BACKEND
    _ensure_dependencies(backend=backend)

    texts = _get_texts_from_documents(documents)

    # Chunk texts using LangChain splitter
    splitter_cls = getattr(_langchain_text_splitter, "RecursiveCharacterTextSplitter")
    splitter = splitter_cls(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    for t in texts:
        # create_documents returns Document objects with page_content attribute
        try:
            docs = splitter.create_documents([t])
            chunks.extend(docs)
        except Exception:
            # fallback: naive split
            chunks.append(t)

    chunk_texts = [getattr(c, "page_content", c) for c in chunks]
    metadatas = [getattr(c, "metadata", {}) or {"source": f"chunk_{i}"} for i, c in enumerate(chunks)]
    ids = [f"{collection_name}_{uuid.uuid4().hex}" for _ in chunk_texts]

    # compute embeddings
    if backend == "sentence_transformers":
        model_cls = getattr(_sentence_transformers, "SentenceTransformer")
        model = model_cls(MODEL_NAME)

        # encode in batches to be memory safe
        embeddings: List[List[float]] = []
        batch_size = 32
        for i in range(0, len(chunk_texts), batch_size):
            batch = chunk_texts[i : i + batch_size]
            embs = model.encode(batch, show_progress_bar=False)
            # sentence-transformers may return numpy arrays
            embeddings.extend([e.tolist() if hasattr(e, "tolist") else list(e) for e in embs])
    else:
        # try OpenAI embeddings via langchain-openai (fallback)
        embeddings = []
        try:
            OpenAIEmbeddings = getattr(_langchain_openai_embeddings, "OpenAIEmbeddings")
        except Exception:
            # some installations use different import path; try langchain.embeddings
            try:
                from langchain.embeddings import OpenAIEmbeddings as OpenAIEmbeddings
            except Exception:
                raise RuntimeError("OpenAI embeddings provider not available in this environment.")

        oe = OpenAIEmbeddings()
        # langchain OpenAIEmbeddings supports embed_documents
        embeddings = oe.embed_documents(chunk_texts)

    # store in chroma
    client = _chromadb.Client(_chromadb_config.Settings(chroma_db_impl="duckdb+parquet", persist_directory=PERSIST_DIR))

    if overwrite:
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass

    collection = client.get_or_create_collection(name=collection_name)

    # Chromadb collection.add accepts documents/metadatas/ids/embeddings depending on version
    try:
        collection.add(documents=chunk_texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
    except TypeError:
        # older/newer chroma variants may expect 'documents' vs 'documents' naming; try alternative signature
        collection.add(documents=chunk_texts, metadata=metadatas, ids=ids, embeddings=embeddings)

    if persist:
        try:
            client.persist()
        except Exception:
            pass

    return collection


def retrieve(query: str, collection_name: str = DEFAULT_COLLECTION, k: int = 3, backend: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve top-k documents for query from Chroma.
    Returns list of dicts: {id, document, metadata, distance}
    """
    backend = backend or EMBEDDING_BACKEND
    _ensure_dependencies(backend=backend)

    # embed query
    if backend == "sentence_transformers":
        model_cls = getattr(_sentence_transformers, "SentenceTransformer")
        model = model_cls(MODEL_NAME)
        q_emb = model.encode([query], show_progress_bar=False)[0]
        q_emb = q_emb.tolist() if hasattr(q_emb, "tolist") else list(q_emb)
    else:
        try:
            OpenAIEmbeddings = getattr(_langchain_openai_embeddings, "OpenAIEmbeddings")
        except Exception:
            try:
                from langchain.embeddings import OpenAIEmbeddings as OpenAIEmbeddings
            except Exception:
                raise RuntimeError("OpenAI embeddings provider not available in this environment.")
        oe = OpenAIEmbeddings()
        q_emb = oe.embed_query(query)

    client = _chromadb.Client(_chromadb_config.Settings(chroma_db_impl="duckdb+parquet", persist_directory=PERSIST_DIR))
    collection = client.get_or_create_collection(name=collection_name)

    results = collection.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas", "distances", "ids"])

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    output: List[Dict[str, Any]] = []
    for i in range(len(docs)):
        output.append({
            "id": ids[i],
            "document": docs[i],
            "metadata": metas[i],
            "distance": dists[i],
        })
    return output


if __name__ == "__main__":
    sample_docs = [
        "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
        "RAG stands for Retrieval-Augmented Generation.",
        "Astrology: basic chart interpretation guidelines for Sun, Moon, Rising."
    ]
    try:
        c = setup_vectorstore(sample_docs, collection_name="aiastro_demo", overwrite=True)
        print("Chroma DB populated (aiastro_demo).")
    except Exception as e:
        print("Failed to populate Chroma DB:", e)
