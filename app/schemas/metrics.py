from pydantic import BaseModel
from typing import Dict, Any

class MetricsResponse(BaseModel):
    status: str
    payload: Dict[str, Any]
    execution_time_ms: float | None = None