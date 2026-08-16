# Ops / Monitoring Dashboard

A read-only operations dashboard for the credit risk default prediction system --
traffic, score distribution, input/covariate drift (PSI), a predictions explorer,
and data-quality checks over `prediction_logs`. Built as a separate system from
the live `/predict` serving path (`credit_risk/api/`); it never writes to
`prediction_logs` and connects with the dedicated `monitoring_reader` DB role.

No ground-truth default labels exist yet, so this dashboard intentionally does
**not** show accuracy, AUC, or calibration -- only what's observable from inputs,
predictions, and traffic.

## Layout

- `backend/` -- FastAPI app (`app/main.py`), reusing `credit_risk.monitoring.log_loader`,
  `credit_risk.monitoring.psi`, and `credit_risk.features` directly rather than
  reimplementing drift/data-loading logic. Runs against the repo-root `.venv`
  (via `uv`) -- no separate Python environment.
- `frontend/` -- Next.js (App Router) + TypeScript + Tailwind + Recharts.

## Running locally

Two processes, both read from the repo-root `.env`:

```bash
# Terminal 1 -- backend (port 8001)
cd dashboard/backend
uv run uvicorn app.main:app --reload --port 8001

# Terminal 2 -- frontend (port 3000)
cd dashboard/frontend
npm run dev
```

Then open http://localhost:3000.

## Drift history (optional)

The Drift Monitoring page's PSI-over-time trend line reads from a `drift_snapshots`
table, populated by an in-process APScheduler job (hourly by default). This needs
a one-time setup step against the RDS instance (requires admin/superuser
credentials the app itself doesn't have):

```bash
psql "$ADMIN_DB_URI" -f ../scripts/sql/create_drift_snapshots_table.sql
```

Then add the resulting connection string to the repo-root `.env`:

```
DRIFT_SNAPSHOT_WRITER_DB_URI=host=... dbname=mlflow user=drift_writer password=...
```

Without this, the dashboard still works fully -- the drift page shows a live
snapshot and the trend panel just reports "not set up yet" instead of erroring.

## Notes

- `credit_risk.monitoring.log_loader.load_prediction_logs()` is reused unmodified.
  On this project's RDS instance, a bare `psycopg2.connect()` was observed taking
  ~85s due to an IPv6/NAT64 DNS fallback delay; `app/config.py` mitigates this
  (without touching the reused function) by pre-resolving the host to IPv4 and
  injecting `hostaddr=` into the DSN -- the same trick already used in
  `credit_risk/monitoring/prediction_logger.py`. This brought it down to ~8s.
- The backend caches the live prediction-log DataFrame and drift report in memory
  with short TTLs (`app/services/cache.py`) rather than hitting Postgres on every
  request -- no Redis/Celery, appropriate for this project's scale.
