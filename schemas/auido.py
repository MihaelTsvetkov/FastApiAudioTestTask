import uuid
from datetime import datetime

from pydantic import BaseModel


class AudioBase(BaseModel):
    filename: str


class AudioUpload(AudioBase):
    pass


class AudioRead(AudioBase):
    id: uuid.UUID
    stored_path: str
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }
