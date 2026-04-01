from typing import AsyncGenerator
from app.infrastructure.http_client import AsyncHttpClient
from app.infrastructure.redis_client import RedisManager
from app.services.aggregator import MetricsAggregator

# Инициализируем синглтоны инфраструктуры
http_client = AsyncHttpClient()
redis_manager = RedisManager()

async def get_http_client() -> AsyncGenerator[AsyncHttpClient, None]:
    yield http_client

async def get_redis_client() -> AsyncGenerator[RedisManager, None]:
    yield redis_manager

def get_metrics_service(
    http: AsyncHttpClient = http_client,
    redis: RedisManager = redis_manager
) -> MetricsAggregator:
    """
    Фабрика для создания сервиса агрегации.
    Здесь происходит внедрение зависимостей (DI).
    """
    return MetricsAggregator(http=http, redis=redis)