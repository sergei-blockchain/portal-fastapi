from fastapi import APIRouter, Depends
from app.services.aggregator import MetricsAggregator
from app.api.deps import get_metrics_service
from app.schemas.metrics import MetricsResponse

router = APIRouter()

@router.get("/current", response_model=MetricsResponse)
async def fetch_metrics(
    service: MetricsAggregator = Depends(get_metrics_service)
):
    import time
    start = time.perf_counter()
    
    data = await service.get_latest_metrics()
    
    return MetricsResponse(
        status="ok",
        payload=data,
        execution_time_ms=round((time.perf_counter() - start) * 1000, 2)
    )