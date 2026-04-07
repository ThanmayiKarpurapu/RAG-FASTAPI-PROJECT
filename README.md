# 🧠 RAG FastAPI Project

## 📌 Overview

This project implements a complete Retrieval-Augmented Generation (RAG) system using:

- FastAPI (Backend API)
- MySQL (Relational Database)
- ChromaDB (Vector Database)
- OpenAI (Embeddings + LLM)
- Streamlit (UI)

The system allows:
- News storage in MySQL
- Vector embedding storage in ChromaDB
- Semantic search retrieval
- LLM-based answer generation
- Chat mode with session memory

<img width="1280" height="710" alt="image" src="https://github.com/user-attachments/assets/9825cdb4-b83e-4ac0-a4f1-df81d74a4c71" />

-FastAPI (demo images)
<img width="1280" height="667" alt="image" src="https://github.com/user-attachments/assets/da2be15f-167c-4eb8-a4db-e92c69d819e1" />
<img width="1274" height="732" alt="image" src="https://github.com/user-attachments/assets/3cd9d5a5-40ee-4e3b-aa2b-165dd3b223b0" />



---

## 🏗️ System Architecture

User → FastAPI → MySQL  
       ↓  
    ChromaDB (Vector DB)  
       ↓  
    OpenAI LLM  

---

## 📂 Project Structure



<img width="320" height="425" alt="image" src="https://github.com/user-attachments/assets/1a1fb30d-4c2b-49f2-a990-29591b103e4a" />


---

## 🔹 Features

### 1️⃣ Database Layer
- POST: Insert single news
- GET: Fetch news by ID
- POST: Bulk import JSON

### 2️⃣ RAG Ingestion
- Chunk text
- Generate embeddings
- Store vectors in ChromaDB

### 3️⃣ Retrieval
- Convert user query to embedding
- Perform cosine similarity search
- Return top-k relevant chunks

### 4️⃣ Generation
- Pass retrieved context to OpenAI LLM
- Generate summarized answer

### 5️⃣ Chat Mode
- Session-based memory
- Stores user history
- Sends full conversation to LLM

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repo
git clone <your_repo_url>


### 2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate


### 3️⃣ Install Dependencies
pip install -r requirements.txt


### 4️⃣ Create .env File
DB_HOST=localhost
DB_USER=root
DB_PASS=yourpassword
DB_NAME=genai
DB_PORT=3306
OPENAI_API_KEY=yourkey


### 5️⃣ Run FastAPI
uvicorn main:app --reload


### 6️⃣ Run Streamlit UI
streamlit run ui_app.py


---

## 📌 Technologies Used

- Python 3.11
- FastAPI
- MySQL
- ChromaDB
- OpenAI API
- Streamlit
- Git

---























