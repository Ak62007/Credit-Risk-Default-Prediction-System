from fastapi import APIRouter, HTTPException, Query

from app.services import drift_service

router = APIRouter(prefix="/api/drift", tags=["drift"])


@router.get("/summary")
def get_drift_summary():
    return drift_service.drift_summary()


@router.get("/feature/{feature_name}")
def get_feature_drift(feature_name: str):
    result = drift_service.feature_distribution(feature_name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown feature '{feature_name}'")
    return result


@router.get("/history")
def get_drift_history(feature: str, days: int = Query(30, ge=1, le=365)):
    if feature not in drift_service.ALL_FEATURES:
        raise HTTPException(status_code=404, detail=f"Unknown feature '{feature}'")
    return drift_service.drift_history(feature=feature, days=days)
