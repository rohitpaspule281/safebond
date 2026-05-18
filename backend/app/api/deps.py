from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.session import get_db_session
from app.services.auth import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    if credentials is None:
        raise UnauthorizedException(detail="Authentication credentials were not provided.")

    payload = decode_access_token(credentials.credentials)
    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedException(detail="Token payload is missing subject.")

    auth_service = AuthService(session)
    user = await auth_service.get_user_by_id(subject)
    if user is None:
        raise UnauthorizedException(detail="Authenticated user no longer exists.")

    return user
