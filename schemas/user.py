import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr | None = None


class UserCreate(UserBase):
    yandex_id: str


class UserRead(UserBase):
    id: uuid.UUID
    is_superuser: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserUpdate(UserBase):
    email: EmailStr | None = None
