import json
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel
from database import get_connection

router = APIRouter(prefix="/news", tags=["news"])


class NewsIn(BaseModel):
    title: str
    body: str
    published_date: Optional[str] = None
    categories: Optional[List[str]] = None


@router.post("")
def create_news(payload: NewsIn):
    conn = get_connection()
    cursor = conn.cursor()

    categories_json = json.dumps(payload.categories or [], ensure_ascii=False)

    cursor.execute(
        """
        INSERT INTO rag (title, body, published_date, categories)
        VALUES (%s, %s, %s, %s)
        """,
        (payload.title, payload.body, payload.published_date, categories_json),
    )
    conn.commit()
    new_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {"message": "Inserted", "id": new_id}


@router.get("/{news_id}")
def get_news(news_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, body, published_date, categories, created_at FROM rag WHERE id=%s",
        (news_id,),
    )
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row or {"error": "News not found"}


@router.post("/import")
async def import_news(file: UploadFile = File(...)):
    raw = await file.read()
    data = json.loads(raw.decode("utf-8"))

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO rag (title, body, published_date, categories)
        VALUES (%s, %s, %s, %s)
    """

    for item in data:
        cursor.execute(
            sql,
            (
                item.get("title"),
                item.get("text"),
                item.get("date"),
                json.dumps(item.get("categories") or []),
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Bulk import completed"}

@router.get("/search")
def search_news(q: str = Query(..., min_length=2), limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, title, published_date
        FROM rag
        WHERE title LIKE %s OR body LIKE %s
        LIMIT %s
        """,
        (f"%{q}%", f"%{q}%", limit)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows