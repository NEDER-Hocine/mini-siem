from collections import Counter
from datetime import date
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, LogEvent
from app.schemas import EventsPerDayResponse, EventsPerDayItem, StatsResponse
from app.utils import threaded_severity_count

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/summary", response_model=StatsResponse)
def get_summary(db: Session = Depends(get_db)) -> StatsResponse:
    """
    Basic aggregated statistics endpoint.
    Demonstrates dicts, Counter, comprehensions and reuse of threaded helper.
    """
    total_logs = db.query(func.count(LogEvent.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0

    # use threaded helper to count per severity
    severity_counts: Dict[str, int] = threaded_severity_count(db)

    # simple per-source aggregation with Counter and comprehension
    rows = db.query(LogEvent.source).all()
    sources = [row[0] for row in rows]
    source_counts = dict(Counter(sources))

    return StatsResponse(
        total_logs=int(total_logs),
        severity_counts=severity_counts,
        source_counts=source_counts,
        total_alerts=int(total_alerts),
    )


@router.get("/events-per-day", response_model=EventsPerDayResponse)
def events_per_day(db: Session = Depends(get_db)) -> EventsPerDayResponse:
    """
    Events grouped by day.
    """
    rows = (
        db.query(func.date(LogEvent.timestamp).label("day"), func.count(LogEvent.id))
        .group_by("day")
        .order_by("day")
        .all()
    )

    items = [
        EventsPerDayItem(date=str(day or date.today()), count=count)
        for day, count in rows
    ]

    return EventsPerDayResponse(items=items)

