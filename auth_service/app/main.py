from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Закрываем соединения после остановки приложения
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

# Подключаем все маршруты аутентификации с префиксом /auth
app.include_router(api_router, prefix="/auth", tags=["auth"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}