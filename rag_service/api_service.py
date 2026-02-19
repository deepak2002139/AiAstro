"""
FastAPI service for the Astrological RAG system
Exposes LangGraph RAG as REST API endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import json
from datetime import datetime
import logging

from langgraph_rag import run_astrology_rag, AstrologyRAGState

# =============================================
# Setup Logging
# =============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================
# Initialize FastAPI App
# =============================================

app = FastAPI(
    title="🌙 Astrology RAG API",
    description="Retrieval-Augmented Generation system for personalized astrological readings",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# Request/Response Models
# =============================================

class AstrologyReadingRequest(BaseModel):
    """Request model for astrological reading."""
    query: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The astrological question or topic"
    )
    zodiac_sign: Optional[str] = Field(
        None,
        description="Zodiac sign for personalized reading (optional)"
    )
    birth_date: Optional[str] = Field(
        None,
        description="Birth date in YYYY-MM-DD format (optional)"
    )
    reading_type: Optional[str] = Field(
        None,
        description="Type of reading: love, career, health, daily, weekly, yearly"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What does the Moon position tell me about my emotional nature?",
                "zodiac_sign": "Aries",
                "reading_type": "personality"
            }
        }


class SourceDocument(BaseModel):
    """Represents a retrieved source document."""
    content: str
    metadata: dict


class AstrologyReadingResponse(BaseModel):
    """Response model for astrological reading."""
    query: str
    reading: str = Field(..., description="The generated astrological reading")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 - 1.0)"
    )
    grounded: bool = Field(
        ...,
        description="Whether the reading is grounded in the knowledge base"
    )
    sources_count: int = Field(
        ...,
        description="Number of source documents used"
    )
    retries: int = Field(
        ...,
        description="Number of retry attempts"
    )
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What does my Aries sun tell me?",
                "reading": "As an Aries, you are...",
                "confidence": 0.85,
                "grounded": True,
                "sources_count": 3,
                "retries": 0,
                "timestamp": "2026-02-20T10:30:00"
            }
        }


class BatchReadingRequest(BaseModel):
    """Request for batch readings."""
    readings: List[AstrologyReadingRequest] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of reading requests"
    )


class BatchReadingResponse(BaseModel):
    """Response for batch readings."""
    total: int
    successful: int
    failed: int
    results: List[AstrologyReadingResponse]
    errors: List[dict] = []


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str


# =============================================
# Request Counter & Rate Limiting (Simple)
# =============================================

class RequestStats:
    """Simple request statistics tracker."""
    def __init__(self):
        self.total_requests = 0
        self.successful = 0
        self.failed = 0

    def record_success(self):
        self.total_requests += 1
        self.successful += 1

    def record_failure(self):
        self.total_requests += 1
        self.failed += 1

    def get_stats(self) -> dict:
        return {
            "total": self.total_requests,
            "successful": self.successful,
            "failed": self.failed,
        }


stats = RequestStats()

# =============================================
# API Endpoints
# =============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/stats")
async def get_stats():
    """Get API statistics."""
    return {
        **stats.get_stats(),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/reading", response_model=AstrologyReadingResponse)
async def generate_reading(request: AstrologyReadingRequest):
    """
    Generate a personalized astrological reading.

    This endpoint uses RAG (Retrieval-Augmented Generation) with LangGraph to:
    1. Retrieve relevant astrological knowledge
    2. Generate a personalized reading
    3. Self-check the response for grounding
    4. Retry if confidence is low
    """
    logger.info(f"Received reading request: {request.query[:50]}...")

    try:
        # Enhance query with context if available
        enhanced_query = request.query
        if request.zodiac_sign:
            enhanced_query += f" (Zodiac: {request.zodiac_sign})"
        if request.reading_type:
            enhanced_query += f" Reading type: {request.reading_type}"

        # Run the RAG pipeline
        result = run_astrology_rag(enhanced_query)

        # Record success
        stats.record_success()

        # Return response
        return AstrologyReadingResponse(
            query=request.query,
            reading=result["answer"],
            confidence=result["confidence"],
            grounded=result["grounded"],
            sources_count=result["sources_count"],
            retries=result["retries"],
        )

    except Exception as e:
        stats.record_failure()
        logger.error(f"Error generating reading: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate reading: {str(e)}"
        )


@app.post("/batch-reading", response_model=BatchReadingResponse)
async def batch_readings(request: BatchReadingRequest):
    """
    Generate multiple astrological readings in batch.
    """
    logger.info(f"Batch reading request with {len(request.readings)} items")

    results = []
    errors = []

    for i, reading_req in enumerate(request.readings):
        try:
            result = run_astrology_rag(reading_req.query)
            results.append(
                AstrologyReadingResponse(
                    query=reading_req.query,
                    reading=result["answer"],
                    confidence=result["confidence"],
                    grounded=result["grounded"],
                    sources_count=result["sources_count"],
                    retries=result["retries"],
                )
            )
            stats.record_success()
        except Exception as e:
            stats.record_failure()
            errors.append({
                "index": i,
                "query": reading_req.query,
                "error": str(e)
            })
            logger.error(f"Batch item {i} failed: {str(e)}")

    return BatchReadingResponse(
        total=len(request.readings),
        successful=len(results),
        failed=len(errors),
        results=results,
        errors=errors
    )


@app.post("/reading-debug")
async def debug_reading(request: AstrologyReadingRequest):
    """
    Debug endpoint that returns detailed RAG pipeline execution info.
    Useful for monitoring and optimization.
    """
    try:
        result = run_astrology_rag(request.query)

        return {
            "query": request.query,
            "reading": result["answer"],
            "debug_info": {
                "confidence": result["confidence"],
                "grounded": result["grounded"],
                "sources_used": result["sources_count"],
                "retry_attempts": result["retries"],
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Debug reading error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# Error Handlers
# =============================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "detail": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }


# =============================================
# Root Endpoint
# =============================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "title": "🌙 Astrology RAG API",
        "version": "1.0.0",
        "description": "LangGraph-powered RAG system for astrological readings",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "generate_reading": "/reading (POST)",
            "batch_readings": "/batch-reading (POST)",
            "debug": "/reading-debug (POST)",
            "docs": "/docs (Swagger UI)",
            "redoc": "/redoc (ReDoc)"
        }
    }


# =============================================
# Startup/Shutdown Events
# =============================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("🌙 Astrology RAG API starting up...")
    logger.info("📚 Knowledge base should be initialized")
    logger.info("✅ API ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"🌙 Astrology RAG API shutting down...")
    logger.info(f"📊 Final stats: {stats.get_stats()}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

