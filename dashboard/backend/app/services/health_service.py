import pandas as pd

from credit_risk.features import CATEGORICAL_COLS
from credit_risk.monitoring.log_loader import NULLABLE_NUMERIC_COLS

from app import deps

# Simple domain-plausibility rules, not derived from the training distribution --
# generous enough to only catch genuinely extreme values (adversarial/stress-test
# inputs), not normal tail behavior.
OUTLIER_RULES = {
    "dti": lambda v: v > 60,
    "pub_rec": lambda v: v > 10,
    "delinq_2yrs": lambda v: v > 8,
    "revol_util": lambda v: v > 100,
}

_EXCLUDED_FROM_DUPLICATE_CHECK = {"id", "request_id", "logged_at", "pred", "prob", "reason_codes", "target"}

# Categories with this many rows or fewer are unstable for any %-based chart (a
# handful of rows can flip their proportion window-to-window). An absolute floor,
# not a percentage -- high-cardinality columns like addr_state (50 categories over
# ~1.9k rows) have plenty of legitimately-small-but-normal categories that a
# percentage threshold would over-flag.
SINGLETON_COUNT_THRESHOLD = 5


def compute_data_health() -> dict:
    df = deps.get_live_df()
    n = len(df)

    null_rates = {col: float(df[col].isna().mean()) for col in NULLABLE_NUMERIC_COLS if col in df.columns}

    singleton_categories = []
    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            continue
        counts = df[col].value_counts()
        for category, count in counts.items():
            if count <= SINGLETON_COUNT_THRESHOLD:
                singleton_categories.append({"feature": col, "category": str(category), "count": int(count)})

    feature_cols = [c for c in df.columns if c not in _EXCLUDED_FROM_DUPLICATE_CHECK]
    dup_mask = df.duplicated(subset=feature_cols, keep=False)
    duplicate_payload_groups = int(df[dup_mask].groupby(feature_cols, dropna=False).ngroups) if dup_mask.any() else 0
    duplicate_payload_extra_rows = int(dup_mask.sum() - duplicate_payload_groups) if dup_mask.any() else 0

    duplicate_logged_at_count = int(df["logged_at"].duplicated(keep=False).sum())

    outliers = []
    for feature, rule in OUTLIER_RULES.items():
        if feature not in df.columns:
            continue
        flagged = df[df[feature].apply(lambda v: pd.notna(v) and rule(v))]
        for row in flagged.head(20).itertuples():
            outliers.append(
                {
                    "request_id": str(row.request_id),
                    "feature": feature,
                    "value": float(getattr(row, feature)),
                }
            )

    logged_at = pd.to_datetime(df["logged_at"])
    distinct_hours = logged_at.dt.floor("h").nunique() if n else 0
    span_hours = (
        int((logged_at.max() - logged_at.min()) / pd.Timedelta(hours=1)) + 1 if n else 0
    )
    traffic_note = (
        f"Requests landed in only {distinct_hours} of {span_hours} hours in the logged window -- "
        "this is scripted load-test traffic (see locustfile.py), not steady production volume."
        if n and distinct_hours and span_hours and distinct_hours / span_hours < 0.5
        else None
    )

    return {
        "null_rates": null_rates,
        "singleton_categories": singleton_categories,
        "duplicate_payload_groups": duplicate_payload_groups,
        "duplicate_payload_extra_rows": duplicate_payload_extra_rows,
        "duplicate_logged_at_count": duplicate_logged_at_count,
        "outliers": outliers,
        "traffic_note": traffic_note,
    }
