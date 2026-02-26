import os
from typing import Dict, List
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from vector_db import get_collection

load_dotenv(".env")

router = APIRouter(prefix="/chat", tags=["chat"])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = "text-embedding-3-large"

def embed_batch(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

LLM_MODEL = "gpt-4o-mini"

# Local in-memory session store (resets if server restarts)
CHAT_SESSIONS: Dict[str, List[dict]] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    top_k: int = 5


@router.post("")
def chat(req: ChatRequest):
    """
    Chat mode:
    - Keeps chat history per session_id
    - Retrieves top_k chunks for each user message
    - Sends: system + retrieved context + full history + new message to LLM
    """
    history = CHAT_SESSIONS.get(req.session_id, [])

    # Retrieve context for the latest user message
    q_vec = embed_batch([req.message])[0]
    res = get_collection().query(
        query_embeddings=[q_vec],
        n_results=req.top_k,
        include=["documents", "metadatas"]
    )

    docs = res["documents"][0]
    metas = res["metadatas"][0]
    context = "\n\n---\n\n".join(docs)

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use retrieved context when relevant."},
        {"role": "system", "content": f"Retrieved context:\n{context}"}
    ]
    messages += history
    messages.append({"role": "user", "content": req.message})

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.2
    )

    answer = completion.choices[0].message.content

    # Update session history
    history = history + [
        {"role": "user", "content": req.message},
        {"role": "assistant", "content": answer}
    ]
    CHAT_SESSIONS[req.session_id] = history

    return {
        "session_id": req.session_id,
        "answer": answer,
        "sources": metas,
        "history_len": len(history)
    }