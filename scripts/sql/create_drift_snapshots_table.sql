-- Dashboard drift-history: a time series of PSI values, populated by the
-- dashboard backend's background snapshot job (dashboard/backend/app/services/drift_snapshot_job.py).
-- Mirrors the reference/target comparison already computed in credit_risk/monitoring/psi.py,
-- just persisted over time instead of computed once and discarded.

CREATE TABLE IF NOT EXISTS drift_snapshots (
    id BIGSERIAL PRIMARY KEY,
    computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    feature TEXT NOT NULL,
    psi DOUBLE PRECISION NOT NULL,
    drift_level TEXT NOT NULL,
    target_label TEXT NOT NULL DEFAULT 'live',
    reference_size INTEGER NOT NULL,
    live_size INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_drift_snapshots_feature_time ON drift_snapshots(feature, computed_at);

-- One-time role setup, mirroring how `monitoring_reader` was created (see
-- notebooks/22_testing_the_logging_function.ipynb, cell 14). `drift_writer` can
-- only INSERT into drift_snapshots -- no access to prediction_logs, no access to
-- any MLflow tracking table on this shared RDS instance.
-- Replace <PASSWORD> before running.
CREATE ROLE drift_writer WITH LOGIN PASSWORD '<PASSWORD>';
GRANT INSERT ON drift_snapshots TO drift_writer;
GRANT USAGE, SELECT ON SEQUENCE drift_snapshots_id_seq TO drift_writer;

-- monitoring_reader already has SELECT on prediction_logs; extend it to also
-- read drift_snapshots so the dashboard's read-only /api/drift/history endpoint
-- can query trend data with the same role it already uses for everything else.
GRANT SELECT ON drift_snapshots TO monitoring_reader;
