import json

import pandas as pd
from fastapi import APIRouter

from credit_risk.config import MODELS_DIR

from app import deps

router = APIRouter(prefix="/api", tags=["overview"])

_METRICS_PATH = MODELS_DIR / "tuned_xgb" / "metrics.json"


@router.get("/overview")
def get_overview():
    live_df = deps.get_live_df()
    now = pd.Timestamp.now()

    with open(_METRICS_PATH) as f:
        metrics = json.load(f)

    prob = live_df["prob"].astype(float)
    logged_at = pd.to_datetime(live_df["logged_at"])

    return {
        "total_logged": int(len(live_df)),
        "requests_last_24h": int((logged_at >= now - pd.Timedelta(hours=24)).sum()),
        "requests_last_1h": int((logged_at >= now - pd.Timedelta(hours=1)).sum()),
        "pred_split": {str(k): int(v) for k, v in live_df["pred"].value_counts().to_dict().items()},
        "prob_percentiles": {
            "p50": float(prob.quantile(0.50)),
            "p90": float(prob.quantile(0.90)),
            "p95": float(prob.quantile(0.95)),
            "p99": float(prob.quantile(0.99)),
            "max": float(prob.max()),
        },
        "current_threshold": metrics["threshold"],
        "model_artifact": str((MODELS_DIR / "tuned_xgb" / "model.pkl").relative_to(MODELS_DIR.parent)),
        "logged_at_range": {
            "min": logged_at.min().isoformat() if len(logged_at) else None,
            "max": logged_at.max().isoformat() if len(logged_at) else None,
        },
        "model_version_note": (
            "prediction_logs has no model-version column today, so served-model "
            "changes over time can't be attributed programmatically."
        ),
    }
