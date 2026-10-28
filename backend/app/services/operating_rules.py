from datetime import datetime, time, timedelta
import unicodedata
from zoneinfo import ZoneInfo

from app.core.config import settings

LOCAL_ZONE = ZoneInfo("America/Sao_Paulo")


def normalized_neighborhood(value: str) -> str:
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c)).casefold().split())


def availability(store, now: datetime | None = None) -> tuple[bool, str | None]:
    current = (now or datetime.now(LOCAL_ZONE)).astimezone(LOCAL_ZONE)
    if not store.is_open or (settings.environment.lower() not in {"development", "test"} and not store.operations_ready):
        return False, None
    if not store.schedule_enabled:
        return current.date().isoformat() not in store.closed_dates, None
    next_start = None
    for offset in range(-1, 8):
        day = current.date() + timedelta(days=offset)
        if day.isoformat() in store.closed_dates:
            continue
        for window in store.opening_hours:
            if window["weekday"] != day.weekday():
                continue
            start = datetime.combine(day, time.fromisoformat(window["opens"]), LOCAL_ZONE)
            end = datetime.combine(day, time.fromisoformat(window["closes"]), LOCAL_ZONE)
            if end <= start:
                end += timedelta(days=1)
            if start <= current < end and current.date().isoformat() not in store.closed_dates:
                return True, None
            if start > current and (next_start is None or start < next_start):
                next_start = start
    return False, next_start.isoformat() if next_start else None
