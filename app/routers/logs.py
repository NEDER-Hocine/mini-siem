from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LogEvent
from app.schemas import LogCreate, LogRead
from app.utils import check_api_key, file_logger, run_detection

router = APIRouter(prefix="/logs", tags=["Logs"])

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(api_key_header)) -> None:
    """
    Simple API-key based protection for write operations.
    """
    if not check_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


@router.get("/", response_model=List[LogRead])
def get_logs(db: Session = Depends(get_db)) -> List[LogRead]:
    """
    Return all logs ordered by newest first.
    """
    logs = db.query(LogEvent).order_by(LogEvent.timestamp.desc()).all()
    return logs


@router.get("/{log_id}", response_model=LogRead)
def get_log(log_id: int, db: Session = Depends(get_db)) -> LogRead:
    log = db.query(LogEvent).filter(LogEvent.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@router.post("/", response_model=LogRead, dependencies=[Depends(require_api_key)])
def add_log(payload: LogCreate, db: Session = Depends(get_db)) -> LogRead:
    """
    Create a new log entry, persist it, then run detection rules.
    Also writes a short audit line to a local file using a context manager.
    """
    log = LogEvent(
        source=payload.source,
        event_type=payload.event_type,
        message=payload.message,
        severity=payload.severity,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # File I/O with context manager (with)
    with file_logger("logs_audit.txt"):
        # triggers our decorator-based function with exception handling
        run_detection(db)

    return log

