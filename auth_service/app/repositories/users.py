from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User


class UsersRepository:
    """Репозиторий для работы с таблицей users."""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_email(self, email: str) -> User | None:
        """Находит пользователя по email"""

        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_id(self, user_id: int) -> User | None:
        """Находит пользователя по id"""

        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def create(self, email: str, password_hash: str, role: str = "user") -> User:
        """Создаёт нового пользователя в БД и возвращает его."""
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user