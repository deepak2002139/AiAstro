"""
LangGraph-based RAG system for astrological readings
Implements a state machine with retrieval, generation, and self-checking
"""

from typing import TypedDict, List, Literal, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END
import os
from pathlib import Path


# =============================================
# STEP 1: Define the State
# =============================================

class AstrologyRAGState(TypedDict):
    """
    Shared state that flows through all nodes in the graph.
    This represents the "memory" of the entire RAG pipeline.
    """
    query: str                          # User's astrological question
    retrieved_docs: List[Document]      # Documents from vector search
    context: str                        # Formatted context from documents
    answer: str                         # Generated astrological reading
    confidence_score: float             # Self-assessed confidence (0.0 - 1.0)
    is_grounded: bool                   # Whether answer is based on knowledge base
    retry_count: int                    # Number of retry attempts
    all_context_used: bool              # Whether we've exhausted context
    metadata: dict                      # Additional metadata


# =============================================
# STEP 2: Initialize LLM and Vector Store
# =============================================

def get_llm(model: str = "gpt-4o", temperature: float = 0.3) -> ChatOpenAI:
    """Initialize the LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)


def get_vectorstore(persist_dir: str = "./chroma_db") -> Chroma:
    """Load or initialize the vector store."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Try to load existing vectorstore
    try:
        vectorstore = Chroma(
            collection_name="astrology_kb",
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
        print("✅ Loaded existing vector store")
        return vectorstore
    except Exception as e:
        print(f"⚠️ Could not load vector store: {e}")
        print("Initialize with: python knowledge_setup.py")
        raise


# =============================================
# STEP 3: Node Functions
# =============================================

def analyze_query(state: AstrologyRAGState) -> AstrologyRAGState:
    """
    NODE 1: Query Analysis
    Analyzes the user's question and decides retrieval strategy.
    """
    print(f"\n🔀 [Node: analyze_query]")
    print(f"   Query: {state['query'][:100]}...")

    # For now, just pass through - in advanced scenarios, we could decompose complex queries
    return state


def retrieve_documents(state: AstrologyRAGState) -> AstrologyRAGState:
    """
    NODE 2: Document Retrieval
    Searches the vector database for relevant astrological knowledge.
    """
    print(f"\n🔍 [Node: retrieve_documents]")

    try:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="mmr",  # Maximal Marginal Relevance for diversity
            search_kwargs={"k": 5, "lambda_mult": 0.5}
        )

        retrieved_docs = retriever.invoke(state["query"])

        # Format context
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"[Source {i}]\n{doc.page_content}")

        context = "\n\n---\n\n".join(context_parts)

        print(f"   📄 Retrieved {len(retrieved_docs)} documents")
        print(f"   📏 Context length: {len(context)} characters")

        return {
            **state,
            "retrieved_docs": retrieved_docs,
            "context": context,
        }
    except Exception as e:
        print(f"   ❌ Retrieval error: {e}")
        return {
            **state,
            "context": "Error retrieving documents. Generating response from base knowledge.",
            "retrieved_docs": [],
        }


def generate_reading(state: AstrologyRAGState) -> AstrologyRAGState:
    """
    NODE 3: Reading Generation
    Generates a personalized astrological reading using the LLM.
    """
    print(f"\n🤖 [Node: generate_reading]")

    llm = get_llm(temperature=0.3)

    # Build the prompt
    prompt = f"""You are an expert astrologer providing personalized, insightful readings.

User Question: {state['query']}

Astrological Knowledge Base:
{state['context']}

Guidelines for your response:
1. Base your answer ONLY on the provided astrological knowledge
2. Be specific and personalized
3. Provide practical guidance
4. Use astrological terminology correctly
5. Mention relevant zodiac signs, planets, or houses where applicable
6. Include timing information if relevant
7. End with a brief affirmation or guidance

Provide a comprehensive astrological reading:"""

    try:
        response = llm.invoke(prompt)
        answer = response.content

        print(f"   ✅ Generated reading ({len(answer)} characters)")

        return {
            **state,
            "answer": answer,
        }
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
        return {
            **state,
            "answer": f"Unable to generate reading: {str(e)}",
        }


def self_check(state: AstrologyRAGState) -> AstrologyRAGState:
    """
    NODE 4: Self-Check & Grounding
    Verifies if the answer is grounded in retrieved documents
    and assesses confidence level.
    """
    print(f"\n✅ [Node: self_check]")

    if not state["retrieved_docs"]:
        print(f"   ⚠️ No documents retrieved - marking as not grounded")
        return {
            **state,
            "is_grounded": False,
            "confidence_score": 0.5,
            "all_context_used": True,
        }

    llm = get_llm(temperature=0)

    # Check if answer is grounded
    grounding_prompt = f"""Analyze whether the following astrological reading is grounded in the provided knowledge base.

Knowledge Base Context:
{state['context'][:2000]}  # Limit to first 2000 chars to avoid token limits

Astrological Reading:
{state['answer'][:1500]}

Respond in JSON format:
{{
    "is_grounded": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Only respond with valid JSON."""

    try:
        response = llm.invoke(grounding_prompt)
        content = response.content

        # Parse response
        import json
        try:
            result = json.loads(content)
            is_grounded = result.get("is_grounded", False)
            confidence = result.get("confidence", 0.5)
            reasoning = result.get("reasoning", "")

            print(f"   📊 Grounded: {is_grounded}, Confidence: {confidence:.2f}")
            print(f"   💭 Reasoning: {reasoning}")
        except json.JSONDecodeError:
            print(f"   ⚠️ Could not parse response, assuming partially grounded")
            is_grounded = "ground" in content.lower()
            confidence = 0.6

        return {
            **state,
            "is_grounded": is_grounded,
            "confidence_score": confidence,
            "all_context_used": True,
        }
    except Exception as e:
        print(f"   ❌ Self-check error: {e}")
        return {
            **state,
            "is_grounded": False,
            "confidence_score": 0.5,
            "all_context_used": True,
        }


# =============================================
# STEP 4: Conditional Edge Logic
# =============================================

def decide_next_step(state: AstrologyRAGState) -> Literal["end", "retrieve_more"]:
    """
    Decides whether to retry retrieval or finish.

    Returns:
        - "end": Answer is good enough, return to user
        - "retrieve_more": Try different retrieval strategy
    """
    # If confidence is high enough, we're done
    if state["confidence_score"] >= 0.7:
        print(f"\n🎯 [Router] High confidence ({state['confidence_score']:.2f}) - ending")
        return "end"

    # If we've tried too many times, give up
    if state["retry_count"] >= 2:
        print(f"\n🎯 [Router] Max retries reached - ending")
        return "end"

    # If context was used and confidence is low, retry
    if state["all_context_used"] and state["confidence_score"] < 0.7:
        print(f"\n🎯 [Router] Low confidence ({state['confidence_score']:.2f}) - retrying retrieval")
        return "retrieve_more"

    return "end"


# =============================================
# STEP 5: Build the Graph
# =============================================

def build_astrology_rag_graph():
    """
    Build the LangGraph workflow for astrological RAG.

    Flow:
    START → analyze_query → retrieve_documents → generate_reading
            → self_check → [decide_next_step] → END or retry loop
    """

    graph = StateGraph(AstrologyRAGState)

    # Add nodes
    graph.add_node("analyze", analyze_query)
    graph.add_node("retrieve", retrieve_documents)
    graph.add_node("generate", generate_reading)
    graph.add_node("self_check", self_check)

    # Add edges
    graph.add_edge(START, "analyze")           # Start → Analyze
    graph.add_edge("analyze", "retrieve")      # Analyze → Retrieve
    graph.add_edge("retrieve", "generate")     # Retrieve → Generate
    graph.add_edge("generate", "self_check")   # Generate → Self-Check

    # Add conditional edge (retry logic)
    graph.add_conditional_edges(
        "self_check",
        decide_next_step,
        {
            "end": END,                # Good confidence → End
            "retrieve_more": "retrieve" # Low confidence → Retry retrieval
        }
    )

    return graph.compile()


# =============================================
# STEP 6: Run the RAG
# =============================================

def run_astrology_rag(query: str, max_retries: int = 2) -> dict:
    """
    Execute the astrological RAG pipeline.

    Args:
        query: User's astrological question
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary with the final result
    """

    print("\n" + "="*70)
    print(f"🌙 ASTROLOGY RAG PIPELINE")
    print(f"📝 Query: {query}")
    print("="*70)

    # Build the graph
    app = build_astrology_rag_graph()

    # Initialize state
    initial_state: AstrologyRAGState = {
        "query": query,
        "retrieved_docs": [],
        "context": "",
        "answer": "",
        "confidence_score": 0.0,
        "is_grounded": False,
        "retry_count": 0,
        "all_context_used": False,
        "metadata": {"max_retries": max_retries}
    }

    # Run the graph
    result = app.invoke(initial_state)

    # Format output
    output = {
        "query": result["query"],
        "answer": result["answer"],
        "confidence": result["confidence_score"],
        "grounded": result["is_grounded"],
        "sources_count": len(result["retrieved_docs"]),
        "retries": result["retry_count"],
    }

    print("\n" + "="*70)
    print(f"✨ RESULT")
    print("="*70)
    print(f"📊 Confidence: {output['confidence']:.2%}")
    print(f"✅ Grounded: {output['grounded']}")
    print(f"📄 Sources: {output['sources_count']}")
    print(f"🔄 Retries: {output['retries']}")
    print("\n📖 Reading:")
    print("-" * 70)
    print(output["answer"])
    print("-" * 70)

    return output


if __name__ == "__main__":
    # Example queries
    test_queries = [
        "What does my Aries sun sign tell me about my personality?",
        "How can Scorpios improve their relationships?",
        "What financial opportunities are coming for Taurus in 2026?",
    ]

    for query in test_queries[:1]:  # Run just the first one
        result = run_astrology_rag(query)

