from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.emergency_contact import EmergencyContact
from app.db.models.user_profile import UserWellnessProfile


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(self, user_id: str) -> UserWellnessProfile | None:
        statement = (
            select(UserWellnessProfile)
            .where(UserWellnessProfile.user_id == user_id)
            .options(selectinload(UserWellnessProfile.emergency_contacts))
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, *, user_id: str) -> UserWellnessProfile:
        profile = UserWellnessProfile(user_id=user_id, current_state_of_mind="")
        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def replace_emergency_contacts(
        self,
        *,
        profile: UserWellnessProfile,
        contacts: list[EmergencyContact],
    ) -> None:
        profile.emergency_contacts.clear()
        await self.session.flush()
        profile.emergency_contacts.extend(contacts)
