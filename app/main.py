import asyncio
import time
from typing import Any, Dict

import httpx
import orjson
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from redis import asyncio as aioredis

app = FastAPI(default_response_class=ORJSONResponse)

EXTERNAL_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
CACHE_TTL = 30

class CircuitBreaker:
    is_open = False
    last_failure_time = 0.0
    failure_threshold = 5.0

async def get_redis():
    pool = aioredis.ConnectionPool.from_url("redis://localhost", decode_responses=True)
    redis = aioredis.Redis(connection_pool=pool)
    try:
        yield redis
    finally:
        await redis.close()

async def get_http_client():
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits, timeout=5.0) as client:
        yield client

async def fetch_data_with_optimization(client: httpx.AsyncClient, redis: aioredis.Redis) -> Dict[str, Any]:
    if CircuitBreaker.is_open:
        if time.time() - CircuitBreaker.last_failure_time < CircuitBreaker.failure_threshold:
            stale_data = await redis.get("external_data")
            if stale_data:
                return orjson.loads(stale_data)
            raise HTTPException(status_code=503, detail="Service Unavailable")
        CircuitBreaker.is_open = False

    cached_data = await redis.get("external_data")
    if cached_data:
        return orjson.loads(cached_data)

    try:
        response = await client.get(EXTERNAL_API_URL)
        response.raise_for_status()
        data = response.json()

        await redis.setex("external_data", CACHE_TTL, orjson.dumps(data))
        return data

    except (httpx.HTTPStatusError, httpx.RequestError):
        CircuitBreaker.is_open = True
        CircuitBreaker.last_failure_time = time.time()
        raise HTTPException(status_code=502, detail="Upstream Error")

@app.get("/api/v1/aggregate")
async def get_aggregated_metrics(
    client: httpx.AsyncClient = Depends(get_http_client),
    redis: aioredis.Redis = Depends(get_redis)
):
    start_time = time.perf_counter()
    result = await fetch_data_with_optimization(client, redis)
    process_time = time.perf_counter() - start_time
    
    return {
        "status": "success",
        "data": result,
        "performance_metrics": {
            "execution_time_ms": round(process_time * 1000, 2),
            "strategy": "cache_aside_circuit_breaker"
        }
    }