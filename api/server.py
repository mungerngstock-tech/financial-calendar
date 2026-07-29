"""
財經行事曆 API Server (FastAPI)
支援靜態檔案服務 + RESTful API

部署：uvicorn api.server:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import date, datetime, timedelta
import json, os

app = FastAPI(title="Financial Calendar API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "events.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/events")
def get_events(
    future_only: bool = Query(True, description="只顯示未來事件"),
    min_importance: int = Query(1, ge=1, le=5),
    category: str | None = Query(None, description="分類篩選"),
    date_from: str | None = Query(None, description="起始日期 YYYY-MM-DD"),
    date_to: str | None = Query(None, description="結束日期 YYYY-MM-DD"),
):
    data = load_data()
    today = date.today().isoformat()
    result = []

    for day in data["events"]:
        if future_only and day["date"] < today:
            continue
        if date_from and day["date"] < date_from:
            continue
        if date_to and day["date"] > date_to:
            continue

        filtered = [
            ev for ev in day["events"]
            if ev["importance"] >= min_importance
            and (category is None or ev["category"] == category)
        ]
        if filtered:
            result.append({"date": day["date"], "day": day["day"], "events": filtered})

    return {"updated": data["updated"], "count": sum(len(d["events"]) for d in result), "events": result}

@app.get("/api/events/today")
def get_today():
    data = load_data()
    today = date.today().isoformat()
    for day in data["events"]:
        if day["date"] == today:
            return {"date": today, "events": day["events"]}
    return {"date": today, "events": []}

@app.get("/api/events/range")
def get_range(days: int = Query(14, ge=1, le=90)):
    data = load_data()
    today = date.today()
    end = today + timedelta(days=days)
    results = [
        day for day in data["events"]
        if today.isoformat() <= day["date"] <= end.isoformat()
    ]
    return {
        "from": today.isoformat(), "to": end.isoformat(),
        "count": sum(len(d["events"]) for d in results),
        "events": results
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
