from fastapi import APIRouter, Depends, Form, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_session
from dependencies import get_current_user
from models.user import User
from models.audio import AudioFile
from schemas.auido import AudioRead
from services.audio_service import save_audio_file

router = APIRouter(prefix="/files", tags=["audio"])


@router.get("", response_model=list[AudioRead])
async def get_user_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> list[AudioRead]:
    result = await db.execute(
        select(AudioFile).where(AudioFile.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/upload", response_model=AudioRead, status_code=201)
async def upload_audio_file(
    filename: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> AudioRead:
    if not file.filename.lower().endswith((".mp3", "wav", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Для загрузки принимаются только аудиофайлы"
        )
    return await save_audio_file(file, filename, current_user, db)
