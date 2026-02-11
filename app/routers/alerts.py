from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert
from app.schemas import AlertRead

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertRead])
def get_alerts(db: Session = Depends(get_db)) -> List[AlertRead]:
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: int, db: Session = Depends(get_db)) -> AlertRead:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

