from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"]
)

# Temporary in-memory storage (later we’ll use DB)
alerts = []
alert_id_counter = 1

@router.get("/")
def get_alerts():
    return alerts

@router.post("/")
def create_alert(type: str, message: str, severity: str = "info"):
    global alert_id_counter
    alert = {
        "id": alert_id_counter,
        "type": type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat()
    }
    alerts.append(alert)
    alert_id_counter += 1
    return alert