from fastapi import APIRouter, HTTPException, Query

from app.services import logs_service

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("")
def list_predictions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    pred: int | None = Query(None, ge=0, le=1),
    min_prob: float | None = Query(None, ge=0, le=1),
    max_prob: float | None = Query(None, ge=0, le=1),
    purpose: str | None = None,
    addr_state: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    return logs_service.list_predictions(
        limit=limit,
        offset=offset,
        pred=pred,
        min_prob=min_prob,
        max_prob=max_prob,
        purpose=purpose,
        addr_state=addr_state,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{request_id}")
def get_prediction(request_id: str):
    result = logs_service.get_prediction(request_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown request_id '{request_id}'")
    return result
