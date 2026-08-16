import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from psycopg2.extras import execute_values

from app import config, deps
from app.services.drift_service import get_drift_report

_scheduler: BackgroundScheduler | None = None

_INSERT_SQL = """
    INSERT INTO drift_snapshots (feature, psi, drift_level, target_label, reference_size, live_size)
    VALUES %s
"""


def take_snapshot() -> None:
    """Computes the current drift report and appends one row per feature to
    drift_snapshots, so the Drift page can show a PSI trend line rather than
    only a live point-in-time snapshot. Requires the one-time table + drift_writer
    role setup (scripts/sql/create_drift_snapshots_table.sql) -- logs and skips
    if that hasn't been done yet, since this is a nice-to-have, not load-bearing.
    """
    if not config.DRIFT_SNAPSHOT_WRITER_DB_URI:
        logger.debug("[drift_snapshot_job] DRIFT_SNAPSHOT_WRITER_DB_URI not set, skipping snapshot")
        return

    try:
        report = get_drift_report()
        reference_size = len(deps.get_reference_df())
        live_size = len(deps.get_live_df())

        rows = [
            (row.feature, float(row.PSI), row.drift_level, "live", reference_size, live_size)
            for row in report.itertuples()
        ]

        conn = psycopg2.connect(config.DRIFT_SNAPSHOT_WRITER_DB_URI)
        try:
            with conn.cursor() as cur:
                execute_values(cur, _INSERT_SQL, rows)
            conn.commit()
        finally:
            conn.close()

        logger.info(f"[drift_snapshot_job] wrote {len(rows)} drift_snapshots rows")
    except Exception as e:
        logger.warning(f"[drift_snapshot_job] failed to write snapshot: {e}")


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if not config.DRIFT_SNAPSHOT_WRITER_DB_URI:
        logger.info("[drift_snapshot_job] writer DB URI not configured -- snapshot history disabled")
        return None
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(take_snapshot, "interval", minutes=config.DRIFT_SNAPSHOT_INTERVAL_MINUTES)
    _scheduler.start()
    logger.info(
        f"[drift_snapshot_job] scheduler started, interval={config.DRIFT_SNAPSHOT_INTERVAL_MINUTES}min"
    )
    # Take one snapshot immediately so trend data starts accumulating right away
    # rather than only after the first full interval.
    _scheduler.add_job(take_snapshot)
    return _scheduler
