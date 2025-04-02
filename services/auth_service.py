from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import user as user_model
from models.user import User
from config import get_settings, Settings

YANDEX_USERINFO_URL = "https://login.yandex.ru/info"


def create_access_token(
    user_id: UUID,
    settings: Optional[Settings] = None
) -> str:
    if settings is None:
        settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    settings: Optional[Settings] = None
) -> str:
    if settings is None:
        settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(
    token: str,
    settings: Optional[Settings] = None
) -> Optional[dict]:
    if settings is None:
        settings = get_settings()
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


async def authenticate_with_yandex(
    code: str,
    session: AsyncSession,
    settings: Optional[Settings] = None
) -> dict:
    if settings is None:
        settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_CLIENT_ID,
                "client_secret": settings.YANDEX_CLIENT_SECRET,
            }
        )

        if resp.status_code != 200:
            raise Exception("Ошибка при получении Яндекс токена")

        data = resp.json()
        yandex_token = data["access_token"]

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            YANDEX_USERINFO_URL,
            params={"format": "json"},
            headers={"Authorization": f"OAuth {yandex_token}"}
        )
        profile = resp.json()

    yandex_id = profile["id"]
    email = profile.get("default_email")

    result = await session.execute(
        select(user_model.User).where(user_model.User.yandex_id == yandex_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = user_model.User(
            yandex_id=yandex_id,
            email=email,
            is_superuser=False
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        if email and user.email != email:
            user.email = email
            await session.commit()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
