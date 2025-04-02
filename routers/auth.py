from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.auth import YandexAuthRequest, RefreshRequest
from services.auth_service import (
    authenticate_with_yandex,
    decode_token,
    create_access_token,
)
from database import get_session
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/yandex/callback")
async def yandex_callback(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> dict:
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code in callback"}

    tokens = await authenticate_with_yandex(code, db)
    return {"status": "Авторизация успешна!", "access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]}


@router.post("/yandex", response_model=dict)
async def yandex_auth(
    data: YandexAuthRequest,
    db: AsyncSession = Depends(get_session)
) -> dict:
    tokens = await authenticate_with_yandex(data.code, db)
    return tokens


@router.post("/refresh")
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_session)
) -> dict:
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Некорректный токен")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_access = create_access_token(user.id)
    return {"access_token": new_access, "token_type": "bearer"}
