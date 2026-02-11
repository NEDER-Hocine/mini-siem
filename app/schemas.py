from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    source: str
    event_type: str  # login, access, error, etc.
    message: str
    severity: str


class LogCreate(LogBase):
    """
    Incoming payload when a client sends a new log/event.
    """


class LogRead(LogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertBase(BaseModel):
    rule_name: str
    severity: str
    description: str
    source: Optional[str] = None


class AlertRead(AlertBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatsResponse(BaseModel):
    total_logs: int
    severity_counts: Dict[str, int]
    source_counts: Dict[str, int]
    total_alerts: int


class EventsPerDayItem(BaseModel):
    date: str
    count: int


class EventsPerDayResponse(BaseModel):
    items: List[EventsPerDayItem]

