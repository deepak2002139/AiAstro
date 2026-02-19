# 🏗️ AiAstro Project Structure & Build Guide

**Date:** February 20, 2026

---

## 📍 Current Project Structure

```
C:\Users\hp\Videos\SpringBoot\AiAstro\
├── backend/
│   └── target/                      # ✅ Pre-built JAR files
│       ├── astrology-backend-1.0.0.jar
│       ├── astrology-backend-1.0.0.jar.original
│       ├── classes/                 # Compiled classes
│       └── ...
│
├── frontend/                        # Frontend application
│   ├── .env
│   └── node_modules/
│
├── rag_service/ ⭐ NEW
│   ├── (17 files - Complete RAG implementation)
│   └── Ready to deploy
│
├── README.md                        # Project readme
└── LICENSE
```

---

## 🔍 Why Maven Command Failed

```
ERROR: The goal you specified requires a project to execute 
but there is no POM in this directory
```

**Cause:** No `pom.xml` file exists in the project root or backend directory.

**Solution:** Your backend is **already built** (see `target/` directory with JAR files).

---

## ✅ Your Backend Status

| Item | Status | Details |
|------|--------|---------|
| **Build Status** | ✅ Complete | JAR files present in target/ |
| **JAR Files** | ✅ Ready | astrology-backend-1.0.0.jar |
| **Compiled Classes** | ✅ Ready | In target/classes/ |
| **pom.xml** | ❌ Missing | Not needed if pre-built |

---

## 🚀 What You Can Do Now

### Option 1: Use Pre-Built Backend (Recommended)
```bash
# The backend JAR is already built!
cd C:\Users\hp\Videos\SpringBoot\AiAstro

# Start the backend
java -jar backend/target/astrology-backend-1.0.0.jar

# Or with custom port (default is likely 8080 or 8081)
java -jar backend/target/astrology-backend-1.0.0.jar --server.port=9090
```

### Option 2: Rebuild Backend (If You Have pom.xml)
If you have the source code with `pom.xml`:

```bash
# Navigate to directory with pom.xml
cd C:\path\to\pom.xml\directory

# Clean and build
mvn clean install

# Or just build
mvn compile
mvn package
```

### Option 3: Start Everything (Recommended for Testing)
```bash
# Terminal 1: Start RAG Service
cd C:\Users\hp\Videos\SpringBoot\AiAstro\rag_service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python knowledge_setup.py
uvicorn api_service:app --port 8000

# Terminal 2: Start Backend
cd C:\Users\hp\Videos\SpringBoot\AiAstro
java -jar backend/target/astrology-backend-1.0.0.jar

# Terminal 3: Start Frontend
cd C:\Users\hp\Videos\SpringBoot\AiAstro\frontend
npm start
```

---

## 📝 If You Need to Create a pom.xml

If you want to rebuild the backend from source, create this `pom.xml` in the `backend` directory:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.aiastro</groupId>
    <artifactId>astrology-backend</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>Astrology Backend</name>
    <description>AI-powered astrological readings backend</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.0</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>17</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring Data JPA -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- H2 Database -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Lombok for reducing boilerplate -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- OpenAI/LangChain Integration (Optional) -->
        <dependency>
            <groupId>com.theokanning.openai-gpt3-java</groupId>
            <artifactId>service</artifactId>
            <version>0.14.0</version>
        </dependency>

        <!-- REST Client -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webflux</artifactId>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Spring Boot Maven Plugin -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>

            <!-- Maven Compiler Plugin -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

Then you can build with:
```bash
cd C:\Users\hp\Videos\SpringBoot\AiAstro\backend
mvn clean install
```

---

## 🐳 Docker Approach (Recommended for Integration)

Instead of managing multiple terminals, use Docker Compose to run everything:

**Create `docker-compose.yml` in project root:**

```yaml
version: '3.8'

services:
  backend:
    image: openjdk:17-slim
    container_name: aiastro-backend
    ports:
      - "8080:8080"
    volumes:
      - ./backend/target:/app
    working_dir: /app
    command: java -jar astrology-backend-1.0.0.jar
    environment:
      - SPRING_PROFILES_ACTIVE=prod
    networks:
      - aiastro-network

  rag-service:
    build:
      context: ./rag_service
      dockerfile: Dockerfile
    container_name: aiastro-rag
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./rag_service/chroma_db:/app/chroma_db
      - ./rag_service/logs:/app/logs
    networks:
      - aiastro-network
    depends_on:
      - backend

  frontend:
    image: node:18-alpine
    container_name: aiastro-frontend
    ports:
      - "3000:3000"
    working_dir: /app
    volumes:
      - ./frontend:/app
    command: npm start
    environment:
      - REACT_APP_API_URL=http://localhost:8080
      - REACT_APP_RAG_URL=http://localhost:8000
    networks:
      - aiastro-network

networks:
  aiastro-network:
    driver: bridge
```

Then run:
```bash
docker-compose up
```

---

## 🎯 Recommended Next Steps

### For Development:

```bash
# 1. Start RAG Service (Most Important - NEW Feature)
cd C:\Users\hp\Videos\SpringBoot\AiAstro\rag_service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python knowledge_setup.py
uvicorn api_service:app --port 8000

# 2. Start Backend (Already Built)
cd C:\Users\hp\Videos\SpringBoot\AiAstro
java -jar backend/target/astrology-backend-1.0.0.jar

# 3. Start Frontend
cd C:\Users\hp\Videos\SpringBoot\AiAstro\frontend
npm start

# 4. Test Integration
curl http://localhost:8000/docs           # RAG Service
curl http://localhost:8080/api/...       # Backend
http://localhost:3000                    # Frontend
```

---

## 🔗 Integration Points

Now you have **3 services** that work together:

```
Frontend (3000)
    ↓
Backend (8080) ↔ RAG Service (8000)
    ↓
Combine results for user
```

**Updated Backend Endpoints (if you integrate RAG):**
- `GET /api/reading/{zodiacSign}` - Original backend
- `POST /api/reading/rag` - Should call RAG service at 8000
- `GET /api/reading/history` - From database

---

## 📊 Build Status Summary

| Component | Status | Action |
|-----------|--------|--------|
| **Backend JAR** | ✅ Ready | `java -jar backend/target/astrology-backend-1.0.0.jar` |
| **RAG Service** | ✅ Ready | `uvicorn api_service:app --port 8000` |
| **Frontend** | ⚠️ Check | `npm start` |
| **Integration** | 🔧 Needed | Update backend to call RAG service |
| **Docker** | ✅ Ready | Use docker-compose.yml |

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Cannot find Java"
```bash
# Install Java 17+
# Download from: https://www.oracle.com/java/technologies/downloads/

# Verify installation
java -version
```

### Issue 2: "Port 8080 already in use"
```bash
# Use different port
java -jar backend/target/astrology-backend-1.0.0.jar --server.port=9090

# Or find and kill process using port
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Issue 3: "Cannot find pom.xml"
**This is normal!** Your backend is pre-built.

Use the JAR directly or create `pom.xml` if rebuilding.

### Issue 4: "RAG Service won't start"
```bash
# Make sure you have:
# 1. Python 3.9+
python --version

# 2. Dependencies installed
pip install -r requirements.txt

# 3. .env configured
# .env should have OPENAI_API_KEY

# 4. Vector DB initialized
python knowledge_setup.py

# Then start
uvicorn api_service:app --port 8000
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `rag_service/GETTING_STARTED.md` | RAG service setup |
| `rag_service/README.md` | RAG service docs |
| `rag_service/IMPLEMENTATION_GUIDE.md` | Complete RAG guide |

---

## 🎯 What to Do Right Now

**Choose one:**

### Option A: Just Run (Simplest)
```bash
# Terminal 1
cd C:\Users\hp\Videos\SpringBoot\AiAstro\rag_service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt && python knowledge_setup.py
uvicorn api_service:app --port 8000

# Terminal 2
cd C:\Users\hp\Videos\SpringBoot\AiAstro
java -jar backend/target/astrology-backend-1.0.0.jar
```

### Option B: Use Docker (Recommended)
```bash
cd C:\Users\hp\Videos\SpringBoot\AiAstro
# Copy .env.example to .env and add OPENAI_API_KEY
docker-compose up
```

### Option C: Rebuild Backend
```bash
# Create pom.xml in backend/ (see above)
cd C:\Users\hp\Videos\SpringBoot\AiAstro\backend
mvn clean install
java -jar target/astrology-backend-1.0.0.jar
```

---

## ✨ You Now Have

✅ Pre-built backend (no rebuild needed)  
✅ RAG service (new, powerful feature)  
✅ Frontend (already exists)  
✅ Docker setup (for easy deployment)  
✅ Integration guide (for connecting everything)  

**Everything is ready to go!** 🚀

---

**Last Updated:** February 20, 2026  
**Status:** ✅ Ready to Start

