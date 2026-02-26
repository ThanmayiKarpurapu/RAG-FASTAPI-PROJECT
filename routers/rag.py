
import os, json
from fastapi import APIRouter, UploadFile, File
from dotenv import load_dotenv
from openai import OpenAI

from database import get_connection
from vector_db import get_collection
from chunking import chunk_text
from pydantic import BaseModel

load_dotenv(".env")

router = APIRouter(prefix="/rag", tags=["rag"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = "text-embedding-3-large"  # best quality

def embed_batch(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


@router.post("/ingest/db")
def ingest_from_db(limit: int = 25, offset: int = 0):
    """
    Reads news from MySQL, chunks body, generates embeddings, stores to ChromaDB.
    Run multiple times with different limits to ingest more.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    #cursor.execute("SELECT id, title, body, published_date FROM rag LIMIT %s", (limit,))
    cursor.execute(
    "SELECT id, title, body, published_date FROM rag ORDER BY id LIMIT %s OFFSET %s",
    (limit, offset))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    collection = get_collection()

    documents = []
    metadatas = []
    ids = []
    MAX_CHUNKS = 2000

    for row in rows:
        news_id = row["id"]
        title = row.get("title") or ""
        body = row.get("body") or ""
        published_date = str(row.get("published_date") or "")

        # combine title + body for better retrieval
        full_text = f"{title}\n\n{body}"
        chunks = chunk_text(full_text)

        for idx, ch in enumerate(chunks):
            doc_id = f"news_{news_id}_chunk_{idx}"
            ids.append(doc_id)
            documents.append(ch)
            metadatas.append({
                "news_id": news_id,
                "title": title,
                "published_date": published_date,
                "chunk_index": idx
            })

    if not documents:
        return {"message": "No documents found to ingest", "count": 0}

    # Embed in batches (avoid huge requests)
    BATCH = 64
    for i in range(0, len(documents), BATCH):
        batch_docs = documents[i:i+BATCH]
        batch_ids = ids[i:i+BATCH]
        batch_meta = metadatas[i:i+BATCH]

        vectors = embed_batch(batch_docs)
        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            embeddings=vectors,
            metadatas=batch_meta
        )

    return {"message": "Ingested from DB to Chroma", "chunks_added": len(documents)}


@router.post("/ingest/file")
async def ingest_from_file(file: UploadFile = File(...)):
    """
    Upload JSON file, chunk+embed, store to ChromaDB.
    JSON format must be a list of objects with keys like: title, text, date, categories
    """
    raw = await file.read()
    data = json.loads(raw.decode("utf-8"))

    if not isinstance(data, list):
        return {"error": "JSON must be a list of objects"}

    collection = get_collection()

    documents, metadatas, ids = [], [], []

    for i, item in enumerate(data):
        title = (item.get("title") or "").strip()
        body = (item.get("text") or item.get("body") or "").strip()
        date = str(item.get("date") or item.get("published_date") or "")

        if not title and not body:
            continue

        full_text = f"{title}\n\n{body}"
        chunks = chunk_text(full_text)

        for idx, ch in enumerate(chunks):
            doc_id = f"file_{file.filename}_item_{i}_chunk_{idx}"
            ids.append(doc_id)
            documents.append(ch)
            metadatas.append({
                "source_file": file.filename,
                "item_index": i,
                "title": title,
                "published_date": date,
                "chunk_index": idx
            })

    if not documents:
        return {"message": "No valid documents found in file", "count": 0}

    BATCH = 32
    for i in range(0, len(documents), BATCH):
        batch_docs = documents[i:i+BATCH]
        batch_ids = ids[i:i+BATCH]
        batch_meta = metadatas[i:i+BATCH]

        vectors = embed_batch(batch_docs)
        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            embeddings=vectors,
            metadatas=batch_meta
        )

    return {"message": "Ingested file to Chroma", "chunks_added": len(documents)}

class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/retrieve")
def retrieve(req: RetrieveRequest):
    """
    Takes a user query, embeds it, and performs semantic search on ChromaDB.
    Returns top_k matched chunks with metadata.
    """
    collection = get_collection()

    q_vec = embed_batch([req.query])[0]

    res = collection.query(
        query_embeddings=[q_vec],
        n_results=req.top_k,
        include=["documents", "metadatas"]
    )

    docs = res["documents"][0]
    metas = res["metadatas"][0]

    return {
        "query": req.query,
        "top_k": req.top_k,
        "results": [{"text": d, "meta": m} for d, m in zip(docs, metas)]
    }

class AskRequest(BaseModel):
    query: str
    top_k: int = 5

LLM_MODEL = "gpt-4o-mini"

@router.post("/ask")
def ask(req: AskRequest):
    """
    Full RAG pipeline:
    1) Embed query
    2) Retrieve top_k chunks
    3) Send to LLM
    4) Return generated answer
    """
    collection = get_collection()

    # Step 1: Embed user question
    q_vec = embed_batch([req.query])[0]

    # Step 2: Retrieve relevant chunks
    res = collection.query(
        query_embeddings=[q_vec],
        n_results=req.top_k,
        include=["documents", "metadatas"]
    )

    docs = res["documents"][0]
    metas = res["metadatas"][0]

    # Step 3: Build context
    context = "\n\n---\n\n".join(
        [f"[{i+1}] {m.get('title','')}\n{d}" for i, (d, m) in enumerate(zip(docs, metas))]
    )

    prompt = f"""
You are a helpful assistant.

Use ONLY the information from the context below.
If the answer is not present in the context, say:
"I don't know based on the provided documents."

User question:
{req.query}

Context:
{context}
"""

    # Step 4: Call LLM
    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    answer = completion.choices[0].message.content

    return {
        "query": req.query,
        "answer": answer,
        "sources": metas
    }