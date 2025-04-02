import os
import uuid
from datetime import datetime, timezone

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from models.audio import AudioFile
from models.user import User


async def save_audio_file(
    file: UploadFile,
    filename: str,
    user: User,
    session: AsyncSession
) -> AudioFile:
    file_id = uuid.uuid4()
    relative_path = os.path.join("media", filename)

    os.makedirs(os.path.dirname(relative_path), exist_ok=True)

    async with aiofiles.open(relative_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    audio = AudioFile(
        id=file_id,
        filename=filename,
        stored_path=str(relative_path),
        user_id=user.id,
        uploaded_at=datetime.now(timezone.utc)
    )

    session.add(audio)
    await session.commit()
    await session.refresh(audio)

    return audio

