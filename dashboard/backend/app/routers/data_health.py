from fastapi import APIRouter

from app.services.health_service import compute_data_health

router = APIRouter(prefix="/api", tags=["data-health"])


@router.get("/data-health")
def get_data_health():
    return compute_data_health()
