"""
Astrological Knowledge Base Setup for RAG
This module initializes the vector store with astrological knowledge
"""

import os
from typing import List
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


def load_knowledge_base() -> str:
    """Load the astrological knowledge base from markdown file."""
    kb_path = Path(__file__).parent / "knowledge_base.md"
    if kb_path.exists():
        with open(kb_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(f"Warning: Knowledge base file not found at {kb_path}")
        return ""


def chunk_knowledge_base(content: str, chunk_size: int = 400, chunk_overlap: int = 100) -> List[Document]:
    """
    Split the knowledge base into manageable chunks.

    Args:
        content: The full knowledge base text
        chunk_size: Maximum characters per chunk
        chunk_overlap: Overlap between chunks for context preservation

    Returns:
        List of Document objects (chunks)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )

    chunks = splitter.split_text(content)

    # Convert to Document objects with metadata
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": "astrology_kb", "chunk_index": i}
        )
        for i, chunk in enumerate(chunks)
    ]

    return documents


def initialize_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    """
    Initialize and populate the vector store with astrological knowledge.

    This function will use local sentence-transformers + chromadb when the
    environment variable USE_LOCAL_EMBEDDINGS=1 is set. Otherwise it uses
    OpenAIEmbeddings (cloud) as before.
    """
    # Load knowledge base
    kb_content = load_knowledge_base()

    if not kb_content:
        raise ValueError("Knowledge base is empty. Please check knowledge_base.md")

    # Split into chunks
    documents = chunk_knowledge_base(kb_content)

    print(f"📚 Loaded {len(documents)} chunks from knowledge base")

    use_local = os.environ.get("USE_LOCAL_EMBEDDINGS", "0") == "1"

    if use_local:
        # Use local sentence-transformers + chromadb via embeddings_transformer
        try:
            from rag_service.embeddings_transformer import setup_vectorstore

            texts = [doc.page_content for doc in documents]
            collection = setup_vectorstore(texts, collection_name="astrology_kb")
            print(f"✅ Local vector store initialized with {len(texts)} documents")
            print(f"📁 Persisted to: {persist_directory} (note: embeddings_transformer defines its own persist dir)")
            return collection
        except Exception as e:
            print("Failed to initialize local embeddings vector store:", e)
            print("Falling back to OpenAIEmbeddings...")

    # Fallback: use OpenAIEmbeddings + Chroma as before
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        show_progress_bar=True
    )

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="astrology_kb",
        persist_directory=persist_directory,
        collection_metadata={"description": "Astrological knowledge base for RAG"}
    )

    print(f"✅ Vector store initialized with {len(documents)} documents")
    print(f"📁 Persisted to: {persist_directory}")

    return vectorstore


def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    """
    Load an existing vector store.

    If USE_LOCAL_EMBEDDINGS=1, this will attempt to load the Chroma collection
    created by the local embeddings flow. Otherwise it will initialize OpenAIEmbeddings
    and load the Chroma wrapper.
    """
    use_local = os.environ.get("USE_LOCAL_EMBEDDINGS", "0") == "1"

    if use_local:
        try:
            # The local chroma persistence is handled in embeddings_transformer (rag_service/chroma_db)
            import chromadb
            from chromadb.config import Settings

            client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=str(Path(__file__).parent / "chroma_db")))
            collection = client.get_collection(name="astrology_kb")
            return collection
        except Exception as e:
            print("Failed to load local chroma collection:", e)
            print("Falling back to OpenAIEmbeddings load path")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma(
        collection_name="astrology_kb",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

    return vectorstore


if __name__ == "__main__":
    # Initialize the vector store
    vs = initialize_vectorstore()

    # Test retrieval
    retriever = vs.as_retriever(search_kwargs={"k": 3})
    test_query = "What are the characteristics of Aries?"
    try:
        results = retriever.invoke(test_query)

        print(f"\n🔍 Test Query: {test_query}")
        print(f"📄 Retrieved {len(results)} documents:")
        for i, doc in enumerate(results, 1):
            print(f"\n  [{i}] {doc.page_content[:200]}...")
    except Exception as e:
        print("Retrieval test failed:", e)
