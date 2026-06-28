from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.db.session import AsyncSessionLocal
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase
from app.core.security import decode_token
from app.core.exceptions import InvalidTokenError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncSession:
    """Создаёт и возвращает асинхронную сессию БД."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_users_repo(db: AsyncSession = Depends(get_db)) -> UsersRepository:
    """Возвращает репозиторий пользователей."""
    return UsersRepository(db)


async def get_auth_uc(db: AsyncSession = Depends(get_db)) -> AuthUseCase:
    """Возвращает объект сценариев аутентификации."""
    return AuthUseCase(db)


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Извлекает user_id из JWT-токена.
    Если токен невалидный или истёк — выбрасывает кастомное исключение.
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError("Token missing 'sub' field")
        return int(user_id)
    
    except JWTError:
        # Ошибка подписи, срока действия и пр
        raise InvalidTokenError("Invalid token")