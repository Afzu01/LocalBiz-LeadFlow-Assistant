import json
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

DB_FILE = Path(__file__).resolve().parent.parent / "leads.db"
UI_FILE = Path(__file__).resolve().parent.parent / "ui" / "index.html"

app = FastAPI(title="LocalBiz LeadFlow Assistant", version="1.0.0")


class LeadEvent(BaseModel):
    name: str
    phone: str
    message: str
    source: str = "whatsapp"


class FollowupUpdate(BaseModel):
    status: str


def conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                message TEXT,
                source TEXT,
                intent TEXT,
                score INTEGER,
                status TEXT DEFAULT 'new',
                created_at TEXT
            )
            """
        )
        c.commit()


def detect_intent(message: str) -> str:
    m = message.lower()
    if any(k in m for k in ["price", "cost", "rate", "quote"]):
        return "pricing"
    if any(k in m for k in ["demo", "book", "schedule", "meeting"]):
        return "booking"
    if any(k in m for k in ["support", "issue", "help", "error"]):
        return "support"
    return "general"


def score_lead(intent: str, message: str) -> int:
    base = {"booking": 90, "pricing": 80, "support": 55, "general": 45}[intent]
    if "urgent" in message.lower():
        base += 10
    return min(base, 100)


init_db()


@app.get("/")
def root() -> dict:
    return {"message": "LocalBiz LeadFlow Assistant", "docs": "/docs", "ui": "/ui"}


@app.get("/ui")
def ui() -> FileResponse:
    return FileResponse(UI_FILE)


@app.post("/webhook/lead")
def receive_lead(payload: LeadEvent) -> dict:
    intent = detect_intent(payload.message)
    score = score_lead(intent, payload.message)
    now = datetime.utcnow().isoformat() + "Z"

    with conn() as c:
        cur = c.execute(
            """
            INSERT INTO leads (name, phone, message, source, intent, score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.name, payload.phone, payload.message, payload.source, intent, score, now),
        )
        c.commit()
        lead_id = cur.lastrowid

    return {"id": lead_id, "intent": intent, "score": score, "status": "new"}


@app.get("/leads")
def list_leads() -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@app.patch("/leads/{lead_id}")
def update_status(lead_id: int, payload: FollowupUpdate) -> dict:
    with conn() as c:
        c.execute("UPDATE leads SET status=? WHERE id=?", (payload.status, lead_id))
        c.commit()
    return {"id": lead_id, "status": payload.status}


@app.get("/summary")
def summary() -> dict:
    with conn() as c:
        rows = c.execute("SELECT score, status, intent FROM leads").fetchall()
    total = len(rows)
    hot = sum(1 for r in rows if r["score"] >= 80)
    open_leads = sum(1 for r in rows if r["status"] in {"new", "contacted"})
    intents = {}
    for r in rows:
        intents[r["intent"]] = intents.get(r["intent"], 0) + 1
    return {"total": total, "hot": hot, "open": open_leads, "intents": intents}
