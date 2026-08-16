import numpy as np
import pandas as pd
import psycopg2

from credit_risk.features import CATEGORICAL_COLS, NUMERICAL_COLS, prep_one_split
from credit_risk.monitoring.psi import build_drift_report

from app import config, deps
from app.services.cache import TTLCache

ALL_FEATURES = NUMERICAL_COLS + CATEGORICAL_COLS


def _load_drift_report() -> pd.DataFrame:
    reference_df = deps.get_reference_df()
    live_df = deps.get_live_df()
    return build_drift_report(reference_df=reference_df, target_df=live_df, target_label="live")


_drift_report_cache: TTLCache[pd.DataFrame] = TTLCache(
    _load_drift_report, ttl_seconds=config.DRIFT_REPORT_CACHE_TTL_SECONDS
)


def get_drift_report() -> pd.DataFrame:
    return _drift_report_cache.get()


def drift_summary() -> dict:
    report = get_drift_report()
    live_size = len(deps.get_live_df())
    reference_size = len(deps.get_reference_df())

    counts = {level: 0 for level in ("stable", "moderate", "significant")}
    counts.update(report["drift_level"].value_counts().to_dict())

    sorted_report = report.sort_values(by="PSI", ascending=False)[["feature", "PSI", "drift_level"]]
    all_features = sorted_report.to_dict(orient="records")
    top_features = all_features[:10]

    return {
        "counts": counts,
        "top_features": top_features,
        "all_features": all_features,
        "reference_size": reference_size,
        "live_size": live_size,
        "sample_size_warning": live_size < config.MIN_LIVE_SAMPLE_SIZE,
        "min_sample_threshold": config.MIN_LIVE_SAMPLE_SIZE,
    }


def _numeric_distribution(reference: pd.Series, live: pd.Series, bins: int = 10) -> dict:
    quantiles = [i * (1 / bins) for i in range(bins + 1)]
    edges = np.nanquantile(reference, q=quantiles)
    edges[0] = -np.inf
    edges[-1] = np.inf

    ref_cuts = pd.cut(reference, bins=edges, duplicates="drop")
    live_cuts = pd.cut(live, bins=edges, duplicates="drop")
    categories = ref_cuts.cat.categories

    ref_props = ref_cuts.value_counts(normalize=True).reindex(categories, fill_value=0.0)
    live_props = live_cuts.value_counts(normalize=True).reindex(categories, fill_value=0.0)

    buckets = []
    for interval, ref_p, live_p in zip(categories, ref_props, live_props):
        buckets.append(
            {
                "range_start": None if np.isneginf(interval.left) else float(interval.left),
                "range_end": None if np.isposinf(interval.right) else float(interval.right),
                "reference_pct": float(ref_p),
                "live_pct": float(live_p),
            }
        )

    return {
        "type": "numeric",
        "buckets": buckets,
        "reference_missing_pct": float(reference.isna().mean()),
        "live_missing_pct": float(live.isna().mean()),
    }


def _categorical_distribution(reference: pd.Series, live: pd.Series) -> dict:
    ref_props = reference.value_counts(normalize=True)
    live_props = live.value_counts(normalize=True)
    categories = sorted(set(ref_props.index) | set(live_props.index))

    unseen = sorted(set(live_props.index) - set(ref_props.index))

    return {
        "type": "categorical",
        "reference_proportions": {c: float(ref_props.get(c, 0.0)) for c in categories},
        "live_proportions": {c: float(live_props.get(c, 0.0)) for c in categories},
        "unseen_categories": unseen,
    }


def feature_distribution(feature: str) -> dict | None:
    if feature not in ALL_FEATURES:
        return None

    reference_features, _ = prep_one_split(deps.get_reference_df())
    live_features, _ = prep_one_split(deps.get_live_df())

    report = get_drift_report()
    row = report[report["feature"] == feature].iloc[0]

    if feature in NUMERICAL_COLS:
        distribution = _numeric_distribution(reference_features[feature], live_features[feature])
    else:
        distribution = _categorical_distribution(reference_features[feature], live_features[feature])

    return {
        "feature": feature,
        "psi": float(row["PSI"]),
        "drift_level": row["drift_level"],
        **distribution,
    }


def drift_history(feature: str, days: int) -> dict:
    """Reads PSI trend points from drift_snapshots, populated by the background
    snapshot job (services/drift_snapshot_job.py). Degrades gracefully to an
    empty series if the table doesn't exist yet (e.g. before the one-time
    drift_writer role/table setup has been run) rather than erroring the page.
    """
    if not config.MONITORING_READER_DB_URI:
        return {"feature": feature, "points": [], "available": False}

    query = """
        SELECT computed_at, psi, drift_level
        FROM drift_snapshots
        WHERE feature = %s AND computed_at >= NOW() - make_interval(days => %s)
        ORDER BY computed_at ASC
    """
    try:
        conn = psycopg2.connect(config.MONITORING_READER_DB_URI)
        try:
            df = pd.read_sql(query, conn, params=(feature, days))
        finally:
            conn.close()
    except Exception:
        # Most likely drift_snapshots doesn't exist yet (table/role/job not set
        # up) -> treat as "no history yet" rather than failing the request.
        return {"feature": feature, "points": [], "available": False}

    points = [
        {"computed_at": row.computed_at.isoformat(), "psi": float(row.psi), "drift_level": row.drift_level}
        for row in df.itertuples()
    ]
    return {"feature": feature, "points": points, "available": True}
