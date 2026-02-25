# 🌙 Astrology RAG Service with LangGraph

**Retrieval-Augmented Generation (RAG) powered by LangGraph for personalized astrological readings**

> Transform your AiAstro application with intelligent, grounded astrological readings using RAG and LangGraph.

---

## 📊 Quick Stats

- **Framework:** LangGraph + LangChain
- **Vector DB:** Chroma
- **API:** FastAPI (REST)
- **Knowledge Base:** Comprehensive astrology knowledge (40+ concepts)
- **Response Quality:** Self-checking with confidence scoring

---

## 🚀 What's Included

### Core Components
- ✅ **LangGraph RAG Pipeline** - State machine with self-checking
- ✅ **Agentic RAG** - Multi-hop retrieval for complex queries
- ✅ **Vector Database** - Chromadb with semantic search
- ✅ **FastAPI Service** - Production-ready REST API
- ✅ **Comprehensive Knowledge Base** - 40+ astrological concepts
- ✅ **Self-Validation** - Built-in confidence scoring and retry logic

### Features
- 🔄 **Automatic Retry** - Low confidence → retrieves again
- 📊 **Confidence Scoring** - 0.0-1.0 quality assessment
- 📚 **Source Tracking** - Know which documents were used
- 🧠 **Query Decomposition** - Break complex questions into sub-queries
- 🎯 **Multi-Hop Retrieval** - Search multiple aspects of knowledge
- 📈 **Observability** - Full logging and statistics

---

## 📦 Quick Start

### 1. Prerequisites
```bash
# Python 3.9+
python --version

# pip (package manager)
pip --version
```

### 2. Installation (5 minutes)

```bash
# 1. Navigate to rag_service directory
cd C:\Users\hp\Videos\SpringBoot\AiAstro\rag_service

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Initialize vector database
python knowledge_setup.py

# 6. Validate setup (optional)
python test_setup.py
```

### 3. Start the Service

```bash
# Terminal 1: Start RAG service
cd rag_service
uvicorn api_service:app --reload --port 8000

# Terminal 2: Test the API
curl -X POST http://localhost:8000/reading \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is my Aries personality like?",
    "zodiac_sign": "Aries"
  }'
```

### 4. Access Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Implementation Guide:** `IMPLEMENTATION_GUIDE.md`

---

## 💡 How It Works

### RAG Pipeline (Simplified)

```
User Question
     ↓
[Retrieve] → Find relevant astrological knowledge
     ↓
[Generate] → Create personalized reading
     ↓
[Check]    → Verify quality & grounding
     ↓
[Confident?] → Yes: Return | No: Retry
     ↓
Final Answer with Sources
```

### Example Query → Response

**Input:**
```json
{
  "query": "As a Scorpio, what are my financial prospects?",
  "zodiac_sign": "Scorpio",
  "reading_type": "finance"
}
```

**Output:**
```json
{
  "query": "As a Scorpio, what are my financial prospects?",
  "reading": "Scorpios are known for their intense focus and strategic thinking...",
  "confidence": 0.92,
  "grounded": true,
  "sources_count": 4,
  "retries": 0
}
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│    Frontend     │ (React/Vue)
│  (Web App)      │
└────────┬────────┘
         │ HTTP/POST
         ▼
┌─────────────────────────────────────────────┐
│          FastAPI Service (port 8000)        │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │  LangGraph RAG Pipeline                │ │
│ │                                         │ │
│ │  Analyze → Retrieve → Generate → Check │ │
│ │                          ↑        │    │ │
│ │                          └────────┘    │ │
│ │          (retry loop)                  │ │
│ └─────────────────────────────────────────┘ │
│                    ↓                         │
│ ┌─────────────────────────────────────────┐ │
│ │  Vector Database (Chroma)               │ │
│ │  - Embeddings of knowledge base         │ │
│ │  - Semantic search capability           │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
         ↓
    JSON Response
```

### Component Details

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Knowledge Base** | Source of truth for astrology | Markdown |
| **Vector DB** | Fast semantic search | Chroma + Embeddings |
| **LLM** | Answer generation | GPT-4o |
| **LangGraph** | Workflow orchestration | Python |
| **API** | REST interface | FastAPI |

---

## 📚 Project Structure

```
rag_service/
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
├── knowledge_base.md             # Astrological knowledge (source)
│
├── knowledge_setup.py            # Vector DB initialization
├── langgraph_rag.py              # Core RAG pipeline
├── agentic_rag.py                # Advanced multi-hop RAG
├── api_service.py                # FastAPI endpoints
├── test_setup.py                 # Validation script
│
├── chroma_db/                    # Vector database (auto-created)
│   ├── data.parquet
│   └── metadata.parquet
│
├── logs/                         # Application logs
│   └── rag_service.log
│
└── README.md                     # This file
```

---

## 🔌 API Reference

### Main Endpoints

#### Generate Reading
```http
POST /reading
Content-Type: application/json
{
  "query": "What is my Aries personality like?",
  "zodiac_sign": "Aries",
  "reading_type": "personality"
}
```

**Response:**
```json
{
  "query": "What is my Aries personality like?",
  "reading": "Aries individuals are...",
  "confidence": 0.88,
  "grounded": true,
  "sources_count": 4,
  "retries": 0,
  "timestamp": "2026-02-20T10:30:00"
}
```

#### Batch Readings
```http
POST /batch-reading
```

#### Health Check
```http
GET /health
```

#### Statistics
```http
GET /stats
```

---

## 🎯 Key Concepts

### RAG (Retrieval-Augmented Generation)
Instead of pure generation, RAG:
1. **Retrieves** relevant information from your knowledge base
2. **Augments** the prompt with that information
3. **Generates** grounded, accurate responses

**Benefits:**
- No hallucinations (grounded in real data)
- Cites sources
- Works with your specific knowledge
- Easier to update knowledge base

### LangGraph
A framework for building stateful workflows:
- **State**: Shared dictionary flowing through all nodes
- **Nodes**: Functions that process the state
- **Edges**: Connections between nodes
- **Conditional Edges**: Smart routing based on state

### Confidence Scoring
Every response gets a confidence score (0.0-1.0):
- `≥0.7`: High confidence ✅ (return to user)
- `0.5-0.7`: Medium confidence (refine answer)
- `<0.5`: Low confidence (retry retrieval)

---

## 🧪 Testing

### Quick Validation

```bash
# Run full validation suite
python test_setup.py

# Output:
# ✅ PASS - Dependencies
# ✅ PASS - Environment
# ✅ PASS - Knowledge Base
# ✅ PASS - Vector Store
# ✅ PASS - RAG Pipeline
# ✅ PASS - API Endpoints
```

### Manual Testing

```bash
# Test health
curl http://localhost:8000/health

# Test reading
curl -X POST http://localhost:8000/reading \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Aries love reading",
    "zodiac_sign": "Aries",
    "reading_type": "love"
  }'

# View statistics
curl http://localhost:8000/stats
```

### Using Swagger UI

1. Start the service: `uvicorn api_service:app --reload`
2. Open browser: http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Fill in parameters
5. Click "Execute"

---

## 🔐 Security

### Environment Variables
```bash
# .env file (never commit to git)
OPENAI_API_KEY=sk-...your-key...
```

### Input Validation
All API inputs validated with Pydantic:
- Query length: 10-500 chars
- Batch size: 1-10 items
- Field types strictly enforced

### Rate Limiting
Recommended production setup:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/reading")
@limiter.limit("100/hour")
async def generate_reading(...):
    ...
```

---

## 📈 Performance

### Response Times (Typical)
- Retrieval: ~500ms
- Generation: ~2-3s
- Self-check: ~1s
- **Total: ~3-5s** per request

### Optimization Tips
1. **Reduce retrieval count**: k=3 instead of k=5
2. **Use faster model**: gpt-3.5-turbo instead of gpt-4o
3. **Add caching**: Cache popular queries
4. **Batch requests**: Process multiple queries in parallel

### Scaling
- Single instance: ~100 requests/minute
- Multi-instance: ~1000+ requests/minute (with load balancer)
- See `IMPLEMENTATION_GUIDE.md` for deployment patterns

---

## 🚢 Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY rag_service/requirements.txt .
RUN pip install -r requirements.txt
COPY rag_service/ .
EXPOSE 8000
CMD ["uvicorn", "api_service:app", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  astrology-rag:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db
```

### Cloud Deployment

**AWS (Lambda + API Gateway):**
```bash
pip install -r requirements.txt -t package/
cd package && zip -r ../deployment.zip . && cd ..
zip -g deployment.zip api_service.py langgraph_rag.py knowledge_setup.py
```

**Azure (App Service):**
```bash
az webapp create --resource-group mygroup --plan myplan \
  --name astrology-rag --runtime "PYTHON|3.11"
```

---

## 🛠️ Troubleshooting

### Common Issues

**Issue: "OPENAI_API_KEY not set"**
```bash
# Check if .env file exists
ls -la .env

# If not, create it
cp .env.example .env

# Edit and add your key
# OPENAI_API_KEY=sk-...
```

**Issue: "Could not load vectorstore"**
```bash
# Reinitialize vector database
python knowledge_setup.py

# Check if chroma_db directory exists
ls -la chroma_db/
```

**Issue: Low confidence scores**
- Knowledge base doesn't cover the topic
- Adjust chunk size in `knowledge_setup.py`
- Add more content to `knowledge_base.md`

**Issue: Slow responses**
- Reduce k=5 to k=3 in `langgraph_rag.py`
- Use gpt-3.5-turbo instead of gpt-4o
- Enable response caching

---

## 📚 Documentation

- **Full Guide:** `IMPLEMENTATION_GUIDE.md` (comprehensive 10,000+ word guide)
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **Code Comments:** Well-documented source files
- **Examples:** Multiple example requests in this README

---

## 🤝 Integration

### Frontend Integration Example (React)

```javascript
import { useState } from 'react';

export function AstrologyReading() {
  const [reading, setReading] = useState('');
  const [loading, setLoading] = useState(false);

  const generateReading = async (query, zodiac) => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/reading', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, zodiac_sign: zodiac })
      });
      const data = await res.json();
      setReading(data.reading);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => generateReading('Aries love?', 'Aries')}>
        Get Reading
      </button>
      {loading && <p>Loading...</p>}
      {reading && <p>{reading}</p>}
    </div>
  );
}
```

---

## 📊 Monitoring

### Access Statistics
```bash
curl http://localhost:8000/stats
# Output:
# {
#   "total": 156,
#   "successful": 153,
#   "failed": 3,
#   "timestamp": "2026-02-20T10:30:00"
# }
```

### Check Logs
```bash
tail -f logs/rag_service.log

# Output:
# 2026-02-20 10:30:45 - API - INFO - Received reading request
# 2026-02-20 10:30:46 - RAG - INFO - Retrieved 5 documents
# 2026-02-20 10:30:47 - RAG - INFO - Generated response
# 2026-02-20 10:30:48 - RAG - INFO - Confidence: 0.92
```

---

## 🎓 Learning Resources

### Concepts Explained in This Project
- **RAG (Retrieval-Augmented Generation)** - How to ground LLMs with data
- **LangGraph** - Building stateful AI workflows
- **Vector Embeddings** - Semantic search fundamentals
- **Self-Checking** - AI quality assurance
- **Agentic RAG** - Multi-step reasoning

### External Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Guide](https://platform.openai.com/docs/guides)
- [Chroma Vector DB](https://docs.trychroma.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

---

## 📝 Knowledge Base Content

The knowledge base includes:
- **12 Zodiac Signs** - Characteristics, elements, ruling planets
- **Planetary Influences** - Sun, Moon, Mercury, Venus, Mars, etc.
- **House System** - 12 life areas
- **Reading Types** - Love, Career, Health, Daily, Weekly, Yearly
- **Transits** - Mercury retrograde, Venus retrograde, etc.
- **Numerology** - Life path numbers
- **Practices** - Daily rituals, seasonal practices

### Updating Knowledge Base

To add more astrological knowledge:

1. Edit `knowledge_base.md`
2. Add content with clear section headers (##, ###)
3. Run: `python knowledge_setup.py`
4. Vector DB automatically updates

---

## 🚀 What's Next?

### Version 2.0 Enhancements
- [ ] Birth chart analysis
- [ ] Real-time planetary positions
- [ ] User profile saving
- [ ] Reading history
- [ ] Multi-language support

### Community Contributions
We welcome contributions! Areas for enhancement:
- Additional astrological knowledge
- Alternative embedding models
- Performance optimizations
- Frontend integration examples

---

## 📄 License

This project is part of the AiAstro application.

---

## 🆘 Support

### Getting Help

1. **Check Documentation**
   - `IMPLEMENTATION_GUIDE.md` - Comprehensive guide
   - http://localhost:8000/docs - API documentation
   - Comments in source code

2. **Run Validation**
   - `python test_setup.py` - Full system check

3. **Check Logs**
   - `logs/rag_service.log` - Application logs

4. **File an Issue**
   - Include error message
   - Include steps to reproduce
   - Include logs from test_setup.py

---

## 📞 Contact

- **Issues:** Check troubleshooting section
- **Questions:** Review implementation guide
- **Feedback:** Consider v2.0 enhancements

---

## 🎉 Ready to Go!

Your Astrology RAG Service is now ready to deploy. Follow the Quick Start section above to get started in 5 minutes!

```bash
# One command to rule them all (after first-time setup):
python -m uvicorn api_service:app --reload --port 8000
```

**Happy readings! 🌙✨**

---

**Last Updated:** February 20, 2026  
**Version:** 1.0.0  
**Framework:** LangGraph + LangChain

