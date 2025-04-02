from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_session
from models.user import User


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Пользователь не аутентифицирован")

    token = auth_header.split(" ")[1]
    settings = request.app.state.settings

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


def require_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return user

