# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "API is working 🚀"}

# @app.get("/hello")
# def hello():
#     return {"message": "Hello from FastAPI 👋"}

# from fastapi import FastAPI, Query
# import os
# import mysql.connector
# from dotenv import load_dotenv

# load_dotenv(".env")

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "Go to /docs"}

# @app.get("/hello")
# def hello():
#     return {"message": "Hello"}

# def get_connection():
#     return mysql.connector.connect(
#         host=os.getenv("DB_HOST", "localhost"),
#         user=os.getenv("DB_USER", "root"),
#         password=os.getenv("DB_PASS", ""),
#         database=os.getenv("DB_NAME", "genai"),
#         port=int(os.getenv("DB_PORT", "3306")),
#     )

# @app.get("/search")
# def search(q: str = Query(..., min_length=2)):
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute(
#         """
#         SELECT id, title
#         FROM rag
#         WHERE title LIKE %s OR body LIKE %s
#         LIMIT 10
#         """,
#         (f"%{q}%", f"%{q}%")
#     )

#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return rows


from fastapi import FastAPI
from routers.news import router as news_router
from routers.rag import router as rag_router
from routers.chat import router as chat_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Go to /docs"}

@app.get("/hello")
def hello():
    return {"message": "Hello"}

# This line connects /news endpoints to the app
app.include_router(news_router)
app.include_router(rag_router)
app.include_router(chat_router)