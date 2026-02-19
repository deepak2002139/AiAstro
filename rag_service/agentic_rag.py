"""
Advanced Agentic RAG for Complex Astrological Queries
Implements multi-hop retrieval, query decomposition, and confidence routing
"""

from typing import TypedDict, List, Literal, Any
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END
import os
import json


# =============================================
# STEP 1: Define Agentic State
# =============================================

class AgenticAstrologyState(TypedDict):
    """
    State for agentic RAG with multi-hop reasoning.
    """
    original_query: str                 # Original user question
    decomposed_queries: List[str]       # Sub-questions broken down from original
    search_round: int                   # Current search iteration
    all_retrieved_docs: List[Document]  # Accumulated documents from all searches
    current_context: str                # Formatted context for current step
    intermediate_answers: List[str]     # Answers to sub-questions
    final_answer: str                   # Synthesized final answer
    confidence: str                     # "high", "medium", "low"
    reasoning_trace: List[str]          # Step-by-step reasoning log
    max_search_rounds: int              # Maximum iterations before stopping


# =============================================
# Helper Functions
# =============================================

def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    """Get initialized LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    return ChatOpenAI(model="gpt-4o", temperature=temperature, api_key=api_key)


def get_vectorstore() -> Chroma:
    """Get vectorstore."""
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    try:
        return Chroma(
            collection_name="astrology_kb",
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )
    except Exception as e:
        raise ValueError(f"Could not load vectorstore: {e}")


# =============================================
# STEP 2: Agentic Nodes
# =============================================

def decompose_query(state: AgenticAstrologyState) -> AgenticAstrologyState:
    """
    NODE 1: Query Decomposition
    Break complex questions into simpler sub-queries for multi-hop retrieval.

    Example:
    Q: "Compare LLMs for astrological AI applications"
    → Q1: "What LLMs are good for AI?"
    → Q2: "What makes a good astrology AI?"
    → Q3: "Comparison of LLMs for astrology"
    """
    print(f"\n🔀 [Node: decompose_query]")
    print(f"   Original: {state['original_query']}")

    llm = get_llm(temperature=0.5)  # Higher temperature for creativity

    prompt = f"""You are an expert at breaking down complex questions into simpler search queries.

Original Question: {state['original_query']}

Break this into 1-4 specific search queries that will help answer the original question.
Each query should be distinct and searchable in an astrology knowledge base.
Return each query on a new line, starting with 'Q:'.

Example format:
Q: What is Aries energy?
Q: How does Mars affect personality?
Q: Fire sign characteristics?"""

    try:
        response = llm.invoke(prompt)
        queries = [
            line.replace("Q:", "").strip()
            for line in response.content.split("\n")
            if line.strip().startswith("Q:")
        ]

        # Always include original query if no decomposition
        if not queries:
            queries = [state["original_query"]]

        print(f"   📋 Decomposed into {len(queries)} queries")
        for i, q in enumerate(queries, 1):
            print(f"      {i}. {q[:60]}...")

        log_msg = f"Decomposed into {len(queries)} sub-queries"

        return {
            **state,
            "decomposed_queries": queries,
            "reasoning_trace": state["reasoning_trace"] + [log_msg],
        }
    except Exception as e:
        print(f"   ❌ Decomposition failed: {e}")
        return {
            **state,
            "decomposed_queries": [state["original_query"]],
            "reasoning_trace": state["reasoning_trace"] + [f"Decomposition failed: {e}"],
        }


def multi_retrieve(state: AgenticAstrologyState) -> AgenticAstrologyState:
    """
    NODE 2: Multi-Hop Retrieval
    Retrieve documents for each decomposed query.
    Uses MMR (Maximal Marginal Relevance) for diversity.
    """
    print(f"\n🔍 [Node: multi_retrieve]")

    try:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "lambda_mult": 0.5}
        )

        all_docs = []
        unique_content = set()

        for query in state["decomposed_queries"]:
            print(f"   🔎 Searching: {query[:50]}...")
            docs = retriever.invoke(query)

            # Add only unique documents
            for doc in docs:
                if doc.page_content not in unique_content:
                    unique_content.add(doc.page_content)
                    all_docs.append(doc)

        print(f"   📄 Retrieved {len(all_docs)} unique documents")

        # Accumulate with previous docs
        combined_docs = state["all_retrieved_docs"] + all_docs

        # Remove duplicates
        seen = set()
        unique_docs = []
        for doc in combined_docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc)

        # Format context
        context_parts = []
        for i, doc in enumerate(unique_docs, 1):
            context_parts.append(f"[Source {i}]\n{doc.page_content}")

        context = "\n\n---\n\n".join(context_parts)

        log_msg = f"Multi-hop retrieval: {len(all_docs)} new docs, {len(unique_docs)} total"

        return {
            **state,
            "all_retrieved_docs": unique_docs,
            "current_context": context,
            "search_round": state["search_round"] + 1,
            "reasoning_trace": state["reasoning_trace"] + [log_msg],
        }
    except Exception as e:
        print(f"   ❌ Retrieval failed: {e}")
        return {
            **state,
            "reasoning_trace": state["reasoning_trace"] + [f"Retrieval failed: {e}"],
        }


def generate_with_confidence(state: AgenticAstrologyState) -> AgenticAstrologyState:
    """
    NODE 3: Generate Answer & Self-Assess
    Generate comprehensive answer and rate confidence level.
    """
    print(f"\n🤖 [Node: generate_with_confidence]")

    llm = get_llm(temperature=0.3)

    prompt = f"""You are an expert astrologer. Using the provided knowledge base, answer the user's question comprehensively.

User's Question: {state['original_query']}

Available Knowledge:
{state['current_context']}

Provide:
1. A comprehensive, personalized answer grounded in astrological principles
2. Rate your confidence level as HIGH, MEDIUM, or LOW based on how well the knowledge base covers the topic
3. Explain your reasoning

Format your response exactly as:
ANSWER:
[Your comprehensive answer here]

CONFIDENCE: [HIGH/MEDIUM/LOW]
CONFIDENCE_REASONING: [Why this confidence level]"""

    try:
        response = llm.invoke(prompt)
        content = response.content

        # Parse response
        parts = content.split("CONFIDENCE:")
        answer = parts[0].replace("ANSWER:", "").strip() if len(parts) > 0 else content

        confidence = "medium"
        if len(parts) > 1:
            conf_text = parts[1].lower()
            if "high" in conf_text:
                confidence = "high"
            elif "medium" in conf_text:
                confidence = "medium"
            else:
                confidence = "low"

        print(f"   ✅ Generated answer, confidence: {confidence}")
        print(f"   📏 Answer length: {len(answer)} chars")

        log_msg = f"Generated answer with {confidence} confidence"

        return {
            **state,
            "final_answer": answer,
            "confidence": confidence,
            "reasoning_trace": state["reasoning_trace"] + [log_msg],
        }
    except Exception as e:
        print(f"   ❌ Generation failed: {e}")
        return {
            **state,
            "final_answer": f"Unable to generate answer: {str(e)}",
            "confidence": "low",
            "reasoning_trace": state["reasoning_trace"] + [f"Generation failed: {e}"],
        }


# =============================================
# STEP 3: Conditional Routing Logic
# =============================================

def confidence_router(state: AgenticAstrologyState) -> Literal["end", "refine", "search_again"]:
    """
    Route based on confidence level and search history.

    Returns:
    - "end": High confidence, answer is ready
    - "refine": Medium confidence, try to improve answer
    - "search_again": Low confidence, do another search round
    """
    print(f"\n🎯 [Router: confidence_router]")
    print(f"   Confidence: {state['confidence']}, Search round: {state['search_round']}")

    if state["confidence"] == "high":
        print(f"   ✅ High confidence - ending")
        return "end"

    if state["search_round"] >= state["max_search_rounds"]:
        print(f"   ⚠️ Max search rounds reached - ending")
        return "end"

    if state["confidence"] == "medium":
        print(f"   🔄 Medium confidence - refining answer")
        return "refine"

    # Low confidence
    if state["search_round"] < state["max_search_rounds"]:
        print(f"   🔍 Low confidence - searching again")
        return "search_again"

    return "end"


def refine_answer(state: AgenticAstrologyState) -> AgenticAstrologyState:
    """
    NODE: Refine Answer
    Improve medium-confidence answers by expanding or clarifying.
    """
    print(f"\n✨ [Node: refine_answer]")

    llm = get_llm(temperature=0.2)

    prompt = f"""You are an expert astrologer. Improve the following answer by making it more comprehensive and confident.

Original Question: {state['original_query']}

Current Answer:
{state['final_answer']}

Additional Context:
{state['current_context'][:1500]}

Expand the answer by:
1. Adding more specific astrological details
2. Including relevant planetary or zodiac information
3. Providing practical guidance
4. Ensuring it's grounded in the provided knowledge

Improved Answer:"""

    try:
        response = llm.invoke(prompt)
        refined = response.content

        print(f"   ✅ Answer refined")

        log_msg = "Refined answer for better clarity"

        return {
            **state,
            "final_answer": refined,
            "confidence": "high",
            "reasoning_trace": state["reasoning_trace"] + [log_msg],
        }
    except Exception as e:
        print(f"   ❌ Refinement failed: {e}")
        return state


# =============================================
# STEP 4: Build Agentic Graph
# =============================================

def build_agentic_rag_graph():
    """
    Build the agentic RAG workflow.

    Flow:
    START → decompose_query → multi_retrieve → generate_with_confidence
            → confidence_router → [refine_answer or search_again or END]
    """

    graph = StateGraph(AgenticAstrologyState)

    # Add nodes
    graph.add_node("decompose", decompose_query)
    graph.add_node("retrieve", multi_retrieve)
    graph.add_node("generate", generate_with_confidence)
    graph.add_node("refine", refine_answer)

    # Add edges
    graph.add_edge(START, "decompose")           # Start → Decompose
    graph.add_edge("decompose", "retrieve")      # Decompose → Retrieve
    graph.add_edge("retrieve", "generate")       # Retrieve → Generate

    # Conditional edge (routing)
    graph.add_conditional_edges(
        "generate",
        confidence_router,
        {
            "end": END,                  # Done
            "refine": "refine",          # Improve answer
            "search_again": "retrieve"   # Another search round
        }
    )

    # Refinement to end
    graph.add_edge("refine", END)

    return graph.compile()


# =============================================
# STEP 5: Run Agentic RAG
# =============================================

def run_agentic_rag(
    query: str,
    max_search_rounds: int = 3,
    verbose: bool = True
) -> dict:
    """
    Execute the agentic RAG pipeline.

    Args:
        query: User's astrological question
        max_search_rounds: Maximum search iterations
        verbose: Print execution trace

    Returns:
        Comprehensive result with reasoning trace
    """

    if verbose:
        print("\n" + "="*70)
        print(f"🌙 AGENTIC ASTROLOGY RAG")
        print(f"📝 Query: {query}")
        print("="*70)

    # Build graph
    app = build_agentic_rag_graph()

    # Initialize state
    initial_state: AgenticAstrologyState = {
        "original_query": query,
        "decomposed_queries": [],
        "search_round": 0,
        "all_retrieved_docs": [],
        "current_context": "",
        "intermediate_answers": [],
        "final_answer": "",
        "confidence": "low",
        "reasoning_trace": ["Agentic RAG pipeline started"],
        "max_search_rounds": max_search_rounds,
    }

    # Run
    result = app.invoke(initial_state)

    # Format output
    output = {
        "query": result["original_query"],
        "answer": result["final_answer"],
        "confidence": result["confidence"],
        "sources_used": len(result["all_retrieved_docs"]),
        "search_rounds": result["search_round"],
        "reasoning_trace": result["reasoning_trace"],
    }

    if verbose:
        print("\n" + "="*70)
        print(f"✨ FINAL RESULT")
        print("="*70)
        print(f"📊 Confidence: {output['confidence'].upper()}")
        print(f"📄 Sources: {output['sources_used']}")
        print(f"🔍 Search Rounds: {output['search_rounds']}")
        print(f"\n🧠 Reasoning Trace:")
        for i, step in enumerate(output["reasoning_trace"], 1):
            print(f"   {i}. {step}")
        print(f"\n📖 Answer:")
        print("-" * 70)
        print(output["answer"])
        print("-" * 70)

    return output


if __name__ == "__main__":
    # Test with a complex query
    complex_query = "How can a Gemini with a Scorpio moon improve their relationships and find career success?"

    result = run_agentic_rag(complex_query, max_search_rounds=3)

