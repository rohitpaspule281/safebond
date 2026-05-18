from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        display_name: str,
        password_hash: str,
        timezone: str,
    ) -> User:
        user = User(
            email=email.lower(),
            display_name=display_name,
            password_hash=password_hash,
            timezone=timezone,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
