import pandas as pd
from fastapi import APIRouter, Query

from app import deps

router = APIRouter(prefix="/api", tags=["traffic"])


@router.get("/traffic/hourly")
def get_hourly_traffic(hours: int = Query(48, ge=1, le=24 * 30)):
    live_df = deps.get_live_df()
    now = pd.Timestamp.now().floor("h")
    window_start = now - pd.Timedelta(hours=hours - 1)

    logged_at = pd.to_datetime(live_df["logged_at"])
    in_window = logged_at[(logged_at >= window_start) & (logged_at <= now + pd.Timedelta(hours=1))]

    hourly_counts = in_window.dt.floor("h").value_counts()
    all_hours = pd.date_range(start=window_start, end=now, freq="h")
    hourly_counts = hourly_counts.reindex(all_hours, fill_value=0).sort_index()

    buckets = [{"hour_start": ts.isoformat(), "count": int(c)} for ts, c in hourly_counts.items()]
    nonzero_hours = int((hourly_counts > 0).sum())
    is_bursty = len(hourly_counts) > 0 and (nonzero_hours / len(hourly_counts)) < 0.3

    return {
        "buckets": buckets,
        "is_bursty": is_bursty,
        "note": (
            "Traffic reflects scripted load-test bursts (see locustfile.py), not "
            "steady production volume -- expect spikes and silent gaps."
            if is_bursty
            else None
        ),
    }
