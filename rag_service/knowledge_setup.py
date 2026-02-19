"""
Astrological Knowledge Base Setup for RAG
This module initializes the vector store with astrological knowledge
"""

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

    Args:
        persist_directory: Directory to persist the Chroma database

    Returns:
        Initialized Chroma vectorstore
    """
    # Load knowledge base
    kb_content = load_knowledge_base()

    if not kb_content:
        raise ValueError("Knowledge base is empty. Please check knowledge_base.md")

    # Split into chunks
    documents = chunk_knowledge_base(kb_content)

    print(f"📚 Loaded {len(documents)} chunks from knowledge base")

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        show_progress_bar=True
    )

    # Create or load vectorstore
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

    Args:
        persist_directory: Directory where Chroma database is persisted

    Returns:
        Loaded Chroma vectorstore
    """
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
    results = retriever.invoke(test_query)

    print(f"\n🔍 Test Query: {test_query}")
    print(f"📄 Retrieved {len(results)} documents:")
    for i, doc in enumerate(results, 1):
        print(f"\n  [{i}] {doc.page_content[:200]}...")

