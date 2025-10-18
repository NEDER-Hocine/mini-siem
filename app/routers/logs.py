from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)

# temporary in-memory storage
logs_db = []

class Log(BaseModel):
    id: int
    source: str
    message: str
    severity: str
    timestamp: datetime

@router.get("/")
def get_logs():
    return {"logs": logs_db}

@router.post("/")
def add_log(log: Log):
    logs_db.append(log.dict())
    return {"message": "Log added successfully", "log": log}
