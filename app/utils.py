from __future__ import annotations

import functools
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from multiprocessing import Manager
from typing import Any, Callable, Dict, Generator, Iterable, List

from sqlalchemy.orm import Session

from app.models import Alert, LogEvent


# -----------------------------------------------------------------------------
# Decorators and context managers
# -----------------------------------------------------------------------------


def exception_safe(func: Callable) -> Callable:
    """
    Simple decorator that catches exceptions and returns a safe dict instead
    of crashing the whole request.
    Demonstrates decorators + exception handling + *args/**kwargs.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - educational on purpose
            return {"error": str(exc), "function": func.__name__}

    return wrapper


@contextmanager
def file_logger(path: str) -> Iterable[None]:
    """
    Context manager around a log file using `with` + file I/O.
    Appends a line with timestamp when entering and leaving the context.
    """
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] -> start block\n")
        try:
            yield
        finally:
            f.write(f"[{datetime.utcnow().isoformat()}] -> end block\n")


# -----------------------------------------------------------------------------
# Detection engine using a Strategy-like design pattern
# -----------------------------------------------------------------------------


class DetectionRule:
    """
    Base detection rule.
    Child classes implement `check` to return a list of Alert objects.
    Demonstrates OOP + inheritance + magic methods.
    """

    name: str = "base-rule"

    def __init__(self, lookback_minutes: int = 5) -> None:
        self.lookback = timedelta(minutes=lookback_minutes)

    def __repr__(self) -> str:
        return f"<DetectionRule name={self.name!r} lookback={self.lookback}>"

    def check(self, db: Session) -> List[Alert]:  # pragma: no cover - example
        raise NotImplementedError


class FailedLoginBurstRule(DetectionRule):
    """
    Example rule:
    "5 failed login events in 5 minutes from same source" -> create alert.
    """

    name = "failed-login-burst"

    def check(self, db: Session) -> List[Alert]:
        now = datetime.utcnow()
        since = now - self.lookback

        recent_logs: List[LogEvent] = (
            db.query(LogEvent)
            .filter(
                LogEvent.timestamp >= since,
                LogEvent.event_type == "login",
                LogEvent.severity == "failed",
            )
            .all()
        )

        # use dict + comprehensions
        per_source: Dict[str, int] = {}
        for log in recent_logs:
            per_source[log.source] = per_source.get(log.source, 0) + 1

        alerts: List[Alert] = []
        for source, count in per_source.items():
            if count >= 5:
                alert = Alert(
                    rule_name=self.name,
                    severity="high",
                    description=f"{count} failed logins in {self.lookback} from {source}",
                    source=source,
                )
                alerts.append(alert)
        return alerts


class BlacklistedIPRule(DetectionRule):
    """
    Simple example of reading a blacklist file via file I/O.
    """

    name = "blacklisted-ip"

    def check(self, db: Session) -> List[Alert]:
        now = datetime.utcnow()
        since = now - self.lookback

        # read set of blacklisted IPs from a text file (one per line)
        try:
            with open("blacklist.txt", "r", encoding="utf-8") as f:
                blacklist = {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            blacklist: set[str] = set()

        recent_logs: List[LogEvent] = (
            db.query(LogEvent).filter(LogEvent.timestamp >= since).all()
        )

        alerts: List[Alert] = []
        for log in recent_logs:
            if log.source in blacklist:
                alert = Alert(
                    rule_name=self.name,
                    severity="critical",
                    description=f"Access from blacklisted IP {log.source}",
                    source=log.source,
                )
                alerts.append(alert)
        return alerts


class DetectionEngine:
    """
    Holds a collection of rules and runs them.
    Demonstrates containers (list / dict), comprehensions, and a basic pattern.
    """

    def __init__(self, *rules: DetectionRule) -> None:
        self._rules: List[DetectionRule] = list(rules)

    def add_rule(self, rule: DetectionRule) -> None:
        self._rules.append(rule)

    def __iter__(self) -> Iterable[DetectionRule]:
        return iter(self._rules)

    def run(self, db: Session) -> List[Alert]:
        # list comprehension with generator expression
        alerts: List[Alert] = [
            alert for rule in self._rules for alert in rule.check(db)
        ]
        return alerts


DETECTION_ENGINE = DetectionEngine(FailedLoginBurstRule(), BlacklistedIPRule())


@exception_safe
def run_detection(db: Session) -> Dict[str, int]:
    """
    Run all configured detection rules and persist generated alerts.
    Returns a tiny summary dictionary.
    """
    generated_alerts: List[Alert] = DETECTION_ENGINE.run(db)

    for alert in generated_alerts:
        db.add(alert)

    db.commit()

    # simple "notification" hook for high / critical alerts
    for alert in generated_alerts:
        if alert.severity in {"high", "critical"}:
            simulate_notification(alert)

    return {"generated_alerts": len(generated_alerts)}


def simulate_notification(alert: Alert) -> None:
    """
    Simulates sending an email/Slack notification by writing to a local file.
    This keeps the project simple but demonstrates the idea clearly.
    """
    line = (
        f"[{datetime.utcnow().isoformat()}] NOTIFY "
        f"{alert.severity.upper()} {alert.rule_name} -> {alert.description}\n"
    )
    with open("notifications.log", "a", encoding="utf-8") as f:
        f.write(line)


# -----------------------------------------------------------------------------
# Generators / iterators + basic concurrency examples
# -----------------------------------------------------------------------------


def iter_recent_logs(db: Session, limit: int = 100) -> Generator[LogEvent, None, None]:
    """
    Generator that lazily yields recent logs, newest first.
    Demonstrates generators / iterators.
    """
    rows = (
        db.query(LogEvent)
        .order_by(LogEvent.timestamp.desc())
        .limit(limit)
        .all()
    )
    for row in rows:
        yield row


def _count_severity_worker(
    logs: List[LogEvent],
    result: Dict[str, int],
    lock: threading.Lock,
) -> None:
    """
    Worker used with threads to accumulate severity counts.
    Demonstrates threading + shared mutable state (dict + lock).
    """
    local_counts: Dict[str, int] = {}
    for log in logs:
        local_counts[log.severity] = local_counts.get(log.severity, 0) + 1

    with lock:
        for sev, count in local_counts.items():
            result[sev] = result.get(sev, 0) + count


def threaded_severity_count(db: Session) -> Dict[str, int]:
    """
    Splits logs into chunks and counts severities using threads.
    """
    all_logs = list(iter_recent_logs(db, limit=1000))
    if not all_logs:
        return {}

    mid = len(all_logs) // 2
    chunks = [all_logs[:mid], all_logs[mid:]]

    shared_result: Dict[str, int] = {}
    lock = threading.Lock()

    threads: List[threading.Thread] = []
    for chunk in chunks:
        t = threading.Thread(
            target=_count_severity_worker,
            args=(chunk, shared_result, lock),
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return shared_result


def multiprocessing_shared_counter_example() -> int:
    """
    Tiny demonstration of processes + shared memory using Manager dict.
    Not used directly by the API, but shows the concept in pure Python.
    """
    with Manager() as manager:
        counter = manager.Value("i", 0)  # shared int between processes

        def _inc_many(n: int) -> None:
            for _ in range(n):
                counter.value += 1

        # This function is intentionally not spawned here to avoid
        # platform-specific multiprocessing issues under web servers.
        # In a standalone script, you could create `Process` objects
        # targeting `_inc_many` and share `counter`.
        _inc_many(10)
        return int(counter.value)


# Simple, hard-coded API key just for demo purposes
API_KEY = "super-secret-mini-siem-key"


def check_api_key(provided: str | None) -> bool:
    return provided == API_KEY

