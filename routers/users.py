from fastapi import APIRouter, Depends

from schemas.user import UserRead
from dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/me", tags=["users"])


@router.get("", response_model=UserRead)
async def read_me(
    current_user: User = Depends(get_current_user)
) -> UserRead:
    return current_user
