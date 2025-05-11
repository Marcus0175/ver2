from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    PASSWORD: str
    ORS_URL: str
    ORS_API_KEY: str
    RATE_PER_KM: float
    BASE_FEE: float
    FREE_SHIPPING_THRESHOLD: float
    ACCEPT_DR_TIMEOUT: int

    model_config = SettingsConfigDict(env_file=f".env")

@lru_cache
def get_settings():
    return Settings()