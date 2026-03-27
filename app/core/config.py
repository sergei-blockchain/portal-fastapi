from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ApexFlow Sentinel"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Инфраструктура
    REDIS_URL: str = "redis://localhost:6379/0"
    EXTERNAL_API_URL: str = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    
    # Настройки Circuit Breaker
    CB_FAILURE_THRESHOLD: float = 5.0
    CACHE_TTL: int = 30

    class Config:
        env_file = ".env"

settings = Settings()