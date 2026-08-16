import os
import socket
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from psycopg2.extensions import parse_dsn

BACKEND_DIR = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = BACKEND_DIR.parent
PROJ_ROOT = DASHBOARD_DIR.parent

# Same repo-root .env used by the rest of the project (credit_risk/config.py).
load_dotenv(PROJ_ROOT / ".env")


def _with_resolved_hostaddr(dsn: str | None) -> str | None:
    """Appends a pre-resolved IPv4 hostaddr to a libpq DSN, same workaround
    already used in credit_risk/monitoring/prediction_logger.py. On this RDS
    instance, letting libpq resolve DNS itself tries an unreachable IPv6/NAT64
    address first and only falls back to IPv4 after a long timeout (observed:
    ~85s vs ~8s with hostaddr pre-resolved) -- this affects every psycopg2
    connection made with the DSN, including inside the reused, unmodified
    load_prediction_logs().
    """
    if not dsn:
        return dsn
    try:
        host = parse_dsn(dsn)["host"]
        ipv4 = socket.gethostbyname(host)
        return f"{dsn} hostaddr={ipv4}"
    except Exception as e:
        logger.warning(f"[config] could not pre-resolve DB host, falling back to plain DSN: {e}")
        return dsn


MONITORING_READER_DB_URI = _with_resolved_hostaddr(os.getenv("MONITORING_READER_DB_URI"))
# Only used by the background drift-snapshot job (services/drift_snapshot_job.py),
# never by the read-only HTTP endpoints. Optional: snapshot history features degrade
# gracefully (empty history, job disabled) if this isn't set yet.
DRIFT_SNAPSHOT_WRITER_DB_URI = _with_resolved_hostaddr(os.getenv("DRIFT_SNAPSHOT_WRITER_DB_URI"))

# credit_risk.monitoring.log_loader.load_prediction_logs() reads this env var
# itself (os.getenv call inside the function) rather than taking a DSN argument,
# so the hostaddr fix above only helps it if we also patch the process env it reads.
if MONITORING_READER_DB_URI:
    os.environ["MONITORING_READER_DB_URI"] = MONITORING_READER_DB_URI

CORS_ORIGINS = [o.strip() for o in os.getenv("DASHBOARD_CORS_ORIGINS", "http://localhost:3000").split(",")]

LIVE_DF_CACHE_TTL_SECONDS = int(os.getenv("DASHBOARD_LIVE_DF_TTL", "60"))
DRIFT_REPORT_CACHE_TTL_SECONDS = int(os.getenv("DASHBOARD_DRIFT_TTL", "120"))

# Below this many live rows, PSI values are unreliable (quantile bins fit on a
# 400k+ row reference set produce nonsense PSI at N~1-2, as seen in notebook 22).
MIN_LIVE_SAMPLE_SIZE = int(os.getenv("DASHBOARD_MIN_LIVE_SAMPLE_SIZE", "30"))

DRIFT_SNAPSHOT_INTERVAL_MINUTES = int(os.getenv("DASHBOARD_SNAPSHOT_INTERVAL_MINUTES", "60"))
