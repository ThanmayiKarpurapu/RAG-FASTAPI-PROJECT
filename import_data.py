import json
import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv(".env")
print("PORT VALUE:", os.getenv("DB_PORT"))

# Get DB details from .env
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT",3306))

# Connect to MySQL
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=DB_PORT
)

cursor = conn.cursor()

# Open your Kaggle JSON file
with open("megarhyme-wikinews.json", "r", encoding="utf-8") as file:
    data = json.load(file)

sql = """
INSERT INTO rag (title, body, published_date, categories)
VALUES (%s, %s, %s, %s)
"""

count = 0

for item in data:
    title = item.get("title", "")
    body = item.get("text", "")
    date = item.get("date", None)
    categories = json.dumps(item.get("categories", []))

    if title and body:
        cursor.execute(sql, (title, body, date, categories))
        count += 1

conn.commit()
cursor.close()
conn.close()

print(f"✅ Imported {count} records successfully!")