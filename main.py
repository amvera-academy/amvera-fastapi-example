from contextlib import asynccontextmanager
import os
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = Path(os.getenv("DATA_DIR", "/data" if os.getenv("AMVERA") else BASE_DIR / "data"))
DATABASE_PATH = DATA_DIR / "items.sqlite3"


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with connect() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="FastAPI on Amvera", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"ok": True, "framework": "FastAPI", "storage": str(DATABASE_PATH)}


@app.get("/api/items")
def get_items():
    with connect() as connection:
        rows = connection.execute("SELECT id, name FROM items ORDER BY id DESC").fetchall()
    items = [dict(row) for row in rows]
    return {"items": items, "count": len(items)}


@app.post("/api/items", status_code=status.HTTP_201_CREATED)
def add_item(item: ItemCreate):
    name = item.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Name must not be empty")
    with connect() as connection:
        cursor = connection.execute("INSERT INTO items (name) VALUES (?)", (name,))
    return {"item": {"id": cursor.lastrowid, "name": name}}


@app.delete("/api/items/{item_id}")
def delete_item(item_id: int):
    with connect() as connection:
        cursor = connection.execute("DELETE FROM items WHERE id = ?", (item_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True, "id": item_id}
