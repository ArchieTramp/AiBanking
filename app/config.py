import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/hexlet",
)

# Параметры пула соединений (пункт 4 задания)
POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "3600"))