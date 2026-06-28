from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.users import UsersRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.schemas.user import UserPublic
from app.schemas.auth import TokenResponse


class AuthUseCase:
    """Сценарии аутентификации: регистрация, логин, профиль."""

    def __init__(self, session: AsyncSession):
        self.repo = UsersRepository(session)

    async def register(self, email: str, password: str) -> UserPublic:

        # Проверяем, не существует ли уже пользователь
        existing = await self.repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()

        # Хешируем пароль и создаём запись
        hashed = hash_password(password)
        user = await self.repo.create(email=email, password_hash=hashed)

        return UserPublic(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )

    async def login(self, email: str, password: str) -> TokenResponse:

        # Ищем пользователя
        user = await self.repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        # Проверяем пароль
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        # Создаём JWT
        token = create_access_token(data={"sub": user.id, "role": user.role})
        return TokenResponse(access_token=token)


    async def me(self, user_id: int) -> UserPublic:
        
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        return UserPublic(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )