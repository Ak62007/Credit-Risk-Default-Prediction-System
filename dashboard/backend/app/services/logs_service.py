import pandas as pd

from app import deps

_LIST_COLUMNS = [
    "request_id",
    "logged_at",
    "pred",
    "prob",
    "purpose",
    "addr_state",
    "loan_amnt",
    "annual_inc",
    "dti",
]


def list_predictions(
    limit: int = 50,
    offset: int = 0,
    pred: int | None = None,
    min_prob: float | None = None,
    max_prob: float | None = None,
    purpose: str | None = None,
    addr_state: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    df = deps.get_live_df().copy()
    df["logged_at"] = pd.to_datetime(df["logged_at"])

    if pred is not None:
        df = df[df["pred"] == pred]
    if min_prob is not None:
        df = df[df["prob"] >= min_prob]
    if max_prob is not None:
        df = df[df["prob"] <= max_prob]
    if purpose is not None:
        df = df[df["purpose"] == purpose]
    if addr_state is not None:
        df = df[df["addr_state"] == addr_state]
    if date_from is not None:
        df = df[df["logged_at"] >= pd.to_datetime(date_from)]
    if date_to is not None:
        df = df[df["logged_at"] <= pd.to_datetime(date_to)]

    df = df.sort_values("logged_at", ascending=False)
    total = len(df)
    page = df.iloc[offset : offset + limit]

    rows = []
    for row in page[_LIST_COLUMNS].itertuples(index=False):
        record = row._asdict()
        record["request_id"] = str(record["request_id"])
        record["logged_at"] = record["logged_at"].isoformat()
        rows.append(record)

    return {"total": int(total), "rows": rows}


def get_prediction(request_id: str) -> dict | None:
    df = deps.get_live_df()
    match = df[df["request_id"].astype(str) == request_id]
    if match.empty:
        return None

    row = match.iloc[0]
    raw_input = row.drop(labels=["id", "request_id", "pred", "prob", "reason_codes", "target"], errors="ignore")

    def _coerce(v):
        if isinstance(v, pd.Timestamp):
            return v.isoformat()
        if pd.isna(v):
            return None
        return v

    return {
        "request_id": str(row["request_id"]),
        "logged_at": row["logged_at"].isoformat() if isinstance(row["logged_at"], pd.Timestamp) else row["logged_at"],
        "issue_d": _coerce(row.get("issue_d")),
        "pred": int(row["pred"]),
        "prob": float(row["prob"]),
        "reason_codes": row["reason_codes"],
        "raw_input": {k: _coerce(v) for k, v in raw_input.items()},
    }
