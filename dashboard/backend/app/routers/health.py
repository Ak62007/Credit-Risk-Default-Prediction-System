import psycopg2
from fastapi import APIRouter

from app import config, deps

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def get_health():
    db_reachable = True
    try:
        # This RDS instance has noticeably slow connection setup from this network
        # (IPv6-then-IPv4 fallback observed to take several seconds) -- a short
        # timeout here would misreport a working DB as "degraded".
        conn = psycopg2.connect(config.MONITORING_READER_DB_URI, connect_timeout=10)
        conn.close()
    except Exception:
        db_reachable = False

    return {
        "status": "ok" if db_reachable else "degraded",
        "db_reachable": db_reachable,
        "reference_loaded": deps.reference_loaded(),
        "last_live_load_at": deps.live_df_loaded_at(),
    }
