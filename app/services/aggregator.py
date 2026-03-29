import time
import orjson
from app.infrastructure.http_client import AsyncHttpClient
from app.infrastructure.redis_client import RedisManager
from app.core.config import settings

class MetricsAggregator:
    _is_open = False
    _last_failure = 0.0

    def __init__(self, http: AsyncHttpClient, redis: RedisManager):
        self.http = http
        self.redis = redis

    async def get_latest_metrics(self):
        # Логика Circuit Breaker
        if self._is_open and (time.time() - self._last_failure < settings.CB_FAILURE_THRESHOLD):
            stale = await self.redis.get("metrics_cache")
            return orjson.loads(stale) if stale else {"error": "circuit_breaker_open"}
        
        self._is_open = False

        # Логика Cache-Aside
        cached = await self.redis.get("metrics_cache")
        if cached:
            return orjson.loads(cached)

        # Запрос данных
        try:
            resp = await self.http.get(settings.EXTERNAL_API_URL)
            resp.raise_for_status()
            data = resp.json()
            
            await self.redis.setex("metrics_cache", settings.CACHE_TTL, orjson.dumps(data))
            return data
        except Exception:
            self._is_open = True
            self._last_failure = time.time()
            raise