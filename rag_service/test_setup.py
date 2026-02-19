#!/usr/bin/env python3
"""
Quick Start & Testing Script for Astrology RAG Service
Run this to validate your setup before deploying
"""

import sys
import os
from pathlib import Path
import subprocess

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def print_step(step_num, text):
    """Print step indicator."""
    print(f"\n[{step_num}] {text}")

def check_dependencies():
    """Check if all required packages are installed."""
    print_step("1", "Checking dependencies...")

    required_packages = [
        "langchain",
        "langgraph",
        "langchain_openai",
        "fastapi",
        "uvicorn",
        "pydantic",
        "chromadb",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install -r requirements.txt")
        return False

    print(f"  ✅ All dependencies installed")
    return True


def check_environment():
    """Check environment variables."""
    print_step("2", "Checking environment variables...")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print(f"  ❌ OPENAI_API_KEY not set")
        print(f"  Add to .env file or export as environment variable")
        return False

    # Mask the key for security
    masked_key = api_key[:8] + "..." + api_key[-4:]
    print(f"  ✅ OPENAI_API_KEY set: {masked_key}")

    return True


def check_knowledge_base():
    """Check if knowledge base exists."""
    print_step("3", "Checking knowledge base...")

    kb_path = Path(__file__).parent / "knowledge_base.md"

    if not kb_path.exists():
        print(f"  ❌ knowledge_base.md not found at {kb_path}")
        return False

    # Check file size
    size_kb = kb_path.stat().st_size / 1024
    print(f"  ✅ knowledge_base.md found ({size_kb:.1f} KB)")

    return True


def check_vector_store():
    """Check if vector store exists and can be loaded."""
    print_step("4", "Checking vector store...")

    try:
        from knowledge_setup import load_vectorstore

        chroma_db_path = Path(__file__).parent / "chroma_db"

        if not chroma_db_path.exists():
            print(f"  ⚠️ Vector store not initialized at {chroma_db_path}")
            print(f"  Run 'python knowledge_setup.py' to initialize")
            return False

        # Try to load it
        vs = load_vectorstore()
        print(f"  ✅ Vector store loaded successfully")

        return True
    except Exception as e:
        print(f"  ❌ Error loading vector store: {e}")
        return False


def test_rag_pipeline():
    """Test the RAG pipeline with a sample query."""
    print_step("5", "Testing RAG pipeline...")

    try:
        from langgraph_rag import run_astrology_rag

        test_query = "What are the key characteristics of Aries?"
        print(f"  Testing with query: {test_query}")

        result = run_astrology_rag(test_query)

        print(f"  ✅ RAG pipeline executed successfully")
        print(f"     - Confidence: {result['confidence']:.2%}")
        print(f"     - Grounded: {result['grounded']}")
        print(f"     - Sources: {result['sources_count']}")
        print(f"     - Answer length: {len(result['answer'])} chars")

        return True
    except Exception as e:
        print(f"  ❌ RAG pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test the FastAPI endpoints."""
    print_step("6", "Testing API endpoints...")

    try:
        import requests
        import time
        from threading import Thread
        from api_service import app
        import uvicorn

        # Start server in background
        def run_server():
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8001,
                log_level="error"
            )

        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()

        # Wait for server to start
        print("  Starting test server...")
        time.sleep(3)

        # Test health endpoint
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ Health check passed")
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Could not connect to server: {e}")
            return False

        # Test reading endpoint
        try:
            payload = {
                "query": "What is Taurus good at?",
                "zodiac_sign": "Taurus"
            }
            response = requests.post(
                "http://127.0.0.1:8001/reading",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Reading endpoint works")
                print(f"     - Confidence: {data['confidence']:.2%}")
                print(f"     - Grounded: {data['grounded']}")
            else:
                print(f"  ❌ Reading endpoint failed: {response.status_code}")
                print(f"     Response: {response.text}")
                return False
        except Exception as e:
            print(f"  ❌ Reading endpoint error: {e}")
            return False

        return True
    except Exception as e:
        print(f"  ⚠️ Could not test API (install requests to test)")
        print(f"     Error: {e}")
        return False


def generate_test_report():
    """Generate comprehensive test report."""
    print_header("ASTROLOGY RAG SERVICE - VALIDATION REPORT")

    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Knowledge Base", check_knowledge_base),
        ("Vector Store", check_vector_store),
        ("RAG Pipeline", test_rag_pipeline),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []

    for name, check_func in checks:
        try:
            passed = check_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            results.append((name, False))

    # Summary
    print_header("SUMMARY")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\n  Passed: {passed_count}/{total_count}\n")

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")

    if passed_count == total_count:
        print(f"\n  🎉 All checks passed! Ready to deploy.")
        print(f"\n  Next steps:")
        print(f"    1. Start server: python -m uvicorn api_service:app --reload --port 8000")
        print(f"    2. Visit API docs: http://localhost:8000/docs")
        print(f"    3. Test endpoints at http://localhost:8000/docs")
    else:
        print(f"\n  ⚠️ Some checks failed. Fix issues above before deploying.")

    print(f"\n{'='*70}\n")

    return passed_count == total_count


def main():
    """Run all checks."""
    try:
        success = generate_test_report()
        return 0 if success else 1
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

