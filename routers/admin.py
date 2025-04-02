from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database import get_session
from models.user import User
from models.audio import AudioFile
from schemas.user import UserRead, UserUpdate
from dependencies import get_current_user, require_superuser

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
async def list_users(
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_session)
) -> list[UserRead]:
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_session)
) -> UserRead:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_session)
) -> UserRead:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", response_class=Response)
async def delete_user(
    user_id: UUID,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_session)
) -> Response:
    await db.execute(delete(AudioFile).where(AudioFile.user_id == user_id))
    user = await db.get(User, user_id)
    if not user:
        return Response(status_code=204)
    await db.delete(user)
    await db.commit()
    return Response(status_code=200)
