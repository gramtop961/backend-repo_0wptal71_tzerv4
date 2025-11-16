import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timezone

from database import db, create_document, get_documents
from schemas import Automation, AutomationRun

app = FastAPI(title="CRM Automations API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "CRM Automations API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Utilities

def _oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid object id")

# Automations endpoints

@app.post("/api/automations", response_model=dict)
def create_automation(payload: Automation):
    inserted_id = create_document("automation", payload)
    return {"id": inserted_id}

@app.get("/api/automations", response_model=List[dict])
def list_automations():
    docs = get_documents("automation")
    # Convert ObjectId to str
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs

# Automation runs

class RunCreate(BaseModel):
    automation_id: str
    notes: Optional[str] = None

@app.post("/api/runs", response_model=dict)
def create_run(payload: RunCreate):
    run = AutomationRun(
        automation_id=payload.automation_id,
        status="running",
        started_at=datetime.now(timezone.utc),
        notes=payload.notes
    )
    inserted_id = create_document("automationrun", run)
    return {"id": inserted_id}

@app.get("/api/runs", response_model=List[dict])
def list_runs():
    docs = get_documents("automationrun")
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs

# Simple stats for dashboard

@app.get("/api/stats", response_model=dict)
def get_stats():
    try:
        total_automations = db["automation"].count_documents({}) if db else 0
        active_automations = db["automation"].count_documents({"status": "active"}) if db else 0
        paused_automations = db["automation"].count_documents({"status": "paused"}) if db else 0
        last_runs = list(db["automationrun"].find({}).sort("started_at", -1).limit(5)) if db else []
        for r in last_runs:
            r["_id"] = str(r["_id"]) if "_id" in r else None
        return {
            "total_automations": total_automations,
            "active_automations": active_automations,
            "paused_automations": paused_automations,
            "recent_runs": last_runs,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
