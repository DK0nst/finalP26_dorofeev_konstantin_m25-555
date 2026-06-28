from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Создаём асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False, 
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)