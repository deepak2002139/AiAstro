# ⚡ Quick Start - AiAstro with RAG Service

**Your project is ready to run!** Here's how:

---

## 🚀 Start Everything in 3 Commands

### Terminal 1: RAG Service (NEW 🎯)
```bash
cd rag_service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python knowledge_setup.py
uvicorn api_service:app --port 8000
```

### Terminal 2: Backend (Already Built ✅)
```bash
java -jar backend/target/astrology-backend-1.0.0.jar
```

### Terminal 3: Frontend
```bash
cd frontend
npm start
```

---

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **RAG Service** | http://localhost:8000/docs | Astrological readings |
| **Backend API** | http://localhost:8080 | Original backend |
| **Frontend** | http://localhost:3000 | Web interface |

---

## 🐳 Or Use Docker (Easier)

```bash
# Make sure .env exists with OPENAI_API_KEY
docker-compose up
```

Then visit:
- Frontend: http://localhost:3000
- RAG API: http://localhost:8000/docs

---

## 📖 Read These Docs

1. **This project structure:** `BUILD_GUIDE.md` (root level)
2. **RAG service setup:** `rag_service/GETTING_STARTED.md`
3. **RAG service docs:** `rag_service/README.md`
4. **Complete RAG guide:** `rag_service/IMPLEMENTATION_GUIDE.md`

---

## ✅ Your Backend

- **Status:** ✅ Already built
- **Location:** `backend/target/astrology-backend-1.0.0.jar`
- **No pom.xml needed:** Pre-built and ready to run

---

## 🎯 What You Get

✅ **Intelligent RAG Service** - Grounds astrological readings in knowledge base  
✅ **Backend API** - Pre-built Spring Boot service  
✅ **Frontend** - React/Vue web interface  
✅ **Docker Setup** - Easy deployment  
✅ **Documentation** - Complete guides included  

---

## 🔧 If You Need Help

| Issue | Solution |
|-------|----------|
| "Cannot find pom.xml" | ✅ Normal - backend is pre-built |
| RAG service won't start | Check: Python 3.9+, dependencies, .env file |
| Backend won't start | Check: Java 17+, port 8080 not in use |
| Frontend won't start | Check: Node.js installed, npm dependencies |

---

## 🌟 Next Steps

**Choose one:**

### Option 1: Development Mode (Multiple Terminals)
Start each service in separate terminal window (see above)

### Option 2: Production Mode (Docker)
```bash
docker-compose up
```

### Option 3: Learn More
Read `BUILD_GUIDE.md` for comprehensive guide

---

**You're all set! 🚀**

Start with Option 1 or Option 2 above and visit http://localhost:3000

---

**For questions:** See `BUILD_GUIDE.md` in this directory

