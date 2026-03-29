import httpx
from app.core.config import settings

class AsyncHttpClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=5.0
        )

    async def get(self, url: str):
        return await self.client.get(url)

    async def close(self):
        await self.client.aclose()

# Синглтон для переиспользования пула соединений
http_client = AsyncHttpClient()