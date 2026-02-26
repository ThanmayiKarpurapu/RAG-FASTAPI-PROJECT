from fastapi import APIRouter
from database import get_connection

router = APIRouter()

@router.get("/search")
def search(q: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title FROM rag WHERE title LIKE %s LIMIT 10",
        (f"%{q}%",)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return rows

@router.get("/article/{id}")
def get_article(id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, body, published_date, categories FROM rag WHERE id=%s",
        (id,)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return row