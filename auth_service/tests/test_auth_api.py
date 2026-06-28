# auth_service/tests/test_auth_api.py

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.api.deps import get_db
from app.db.base import Base
from app.core.security import create_access_token
from app.core.config import settings


# Подготовка in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    """Тестовая зависимость для сессии БД."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(autouse=True)
async def setup_db():
    """Создаёт таблицы перед всеми тестами и удаляет после (в рамках сессии)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client():
    """Асинхронный HTTP-клиент с переопределённой зависимостью БД."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


class TestAuthAPI:
    """Интеграционные тесты эндпоинтов аутентификации."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient):
        """Успешная регистрация возвращает 201 и данные пользователя."""
        payload = {
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
        response = await async_client.post("/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert data["role"] == "user"
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient):
        """Повторная регистрация с тем же email возвращает 409."""
        payload = {
            "email": "duplicate@example.com",
            "password": "password123"
        }
        # Первая попытка — успех
        await async_client.post("/auth/register", json=payload)
        # Вторая попытка — конфликт
        response = await async_client.post("/auth/register", json=payload)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """Успешный логин с правильными учётными данными."""
        # Сначала регистрируем пользователя
        await async_client.post(
            "/auth/register",
            json={"email": "login@example.com", "password": "testpass"}
        )
        # Логинимся через OAuth2 форму
        form_data = {
            "username": "login@example.com",
            "password": "testpass"
        }
        response = await async_client.post("/auth/login", data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient):
        """Логин с неверным паролем возвращает 401."""
        await async_client.post(
            "/auth/register",
            json={"email": "wrong@example.com", "password": "correctpass"}
        )
        form_data = {
            "username": "wrong@example.com",
            "password": "incorrectpass"
        }
        response = await async_client.post("/auth/login", data=form_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_valid_token(self, async_client: AsyncClient):
        """Получение профиля с валидным токеном."""
        # Регистрируем и получаем токен через логин
        await async_client.post(
            "/auth/register",
            json={"email": "me@example.com", "password": "mypassword"}
        )
        login_resp = await async_client.post(
            "/auth/login",
            data={"username": "me@example.com", "password": "mypassword"}
        )
        token = login_resp.json()["access_token"]

        # Запрос /auth/me с токеном
        response = await async_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["role"] == "user"

    @pytest.mark.asyncio
    async def test_me_without_token(self, async_client: AsyncClient):
        """Запрос /auth/me без токена возвращает 401."""
        response = await async_client.get("/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_invalid_token(self, async_client: AsyncClient):
        """Запрос /auth/me с поддельным токеном возвращает 401."""
        response = await async_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401