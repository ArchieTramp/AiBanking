from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import (
    DATABASE_URL,
    MAX_OVERFLOW,
    POOL_RECYCLE,
    POOL_SIZE,
    POOL_TIMEOUT,
)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""


# Движок создаётся ОДИН раз на всё приложение.
# Именно здесь настраивается пул соединений (пункт 4).
engine = create_async_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=300,          # оставляем, это работает
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "tcp_keepalives_idle": "600",
            "tcp_keepalives_interval": "30",
            "tcp_keepalives_count": "10",
        }
    },
    echo=False,
)

# Фабрика сессий: каждый запрос получает свою AsyncSession из пула
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    """FastAPI-зависимость: выдаёт сессию и гарантированно закрывает её."""
    async with AsyncSessionLocal() as session:
        yield session


def get_pool_status() -> dict:
    """Диагностика пула — пригодится для /ready или отладки."""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
    }