from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.routers import alerts

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)

# temporary in-memory storage
logs_db = []

class Log(BaseModel):
    source: str
    message: str
    severity: str

@router.get("/")
def get_logs():
    return {"logs": logs_db}

@router.post("/")
def add_log(log: Log):
    # auto-generate id
    log_id = len(logs_db) + 1
    # auto-generate timestamp
    timestamp = datetime.utcnow().isoformat()
    
    log_entry = {
        "id": log_id,
        "source": log.source,
        "message": log.message,
        "severity": log.severity,
        "timestamp": timestamp
    }

    # save the log
    logs_db.append(log_entry)

    # 🚨 Auto-create alert if severity is critical
    if log.severity.lower() == "critical":
        alert_entry = {
            "id": len(alerts.alerts) + 1,
            "type": "Critical Log Alert",
            "message": f"[{log.source}] {log.message}",
            "severity": "critical",
            "timestamp": datetime.utcnow().isoformat()
        }
        alerts.alerts.append(alert_entry)

    return {"message": "Log added successfully", "log": log_entry}

