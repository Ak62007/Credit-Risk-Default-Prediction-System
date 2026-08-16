import json

import numpy as np
from fastapi import APIRouter, Query

from credit_risk.config import MODELS_DIR

from app import deps

router = APIRouter(prefix="/api", tags=["scores"])


@router.get("/scores/distribution")
def get_score_distribution(bins: int = Query(30, ge=5, le=100)):
    live_df = deps.get_live_df()
    prob = live_df["prob"].astype(float).dropna()

    with open(MODELS_DIR / "tuned_xgb" / "metrics.json") as f:
        threshold = json.load(f)["threshold"]

    counts, edges = np.histogram(prob, bins=bins, range=(0.0, 1.0))
    buckets = [
        {"range_start": float(edges[i]), "range_end": float(edges[i + 1]), "count": int(counts[i])}
        for i in range(len(counts))
    ]

    return {
        "buckets": buckets,
        "threshold": threshold,
        "mean": float(prob.mean()) if len(prob) else None,
        "median": float(prob.median()) if len(prob) else None,
    }
