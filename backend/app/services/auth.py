from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from app.schemas.user import UserPublic


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(self, payload: UserRegisterRequest) -> TokenResponse:
        existing = await self.users.get_by_email(payload.email)
        if existing is not None:
            raise ConflictException(detail="An account with that email already exists.")

        try:
            user = await self.users.create(
                email=payload.email,
                display_name=payload.display_name,
                password_hash=hash_password(payload.password),
                timezone=payload.timezone,
            )
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictException(detail="An account with that email already exists.") from exc

        token, expires_in = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user=UserPublic.model_validate(user),
        )

    async def login(self, payload: UserLoginRequest) -> TokenResponse:
        user = await self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException(detail="Incorrect email or password.")

        token, expires_in = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user=UserPublic.model_validate(user),
        )

    async def get_user_by_id(self, user_id: str):
        return await self.users.get_by_id(user_id)
