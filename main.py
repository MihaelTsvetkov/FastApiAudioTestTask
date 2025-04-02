import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from config import get_settings, Settings
from database import get_session
from models.user import User
from services.auth_service import create_access_token
from routers import auth, users, admin, audio

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

templates = Jinja2Templates(directory="templates")


def get_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await asyncio.sleep(2)

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.yandex_id == "manual_superuser")
            )
            user = result.scalars().first()
            if user:
                token = create_access_token(user_id=str(user.id))
                logger.info("SUPERUSER ACCESS TOKEN:\n%s", token)
            else:
                logger.warning("Superuser not found!")
            break

        yield

    return lifespan


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    if settings is None:
        settings = get_settings()

    app = FastAPI(lifespan=get_lifespan(settings))

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(admin.router)
    app.include_router(audio.router)

    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("login.html", {"request": request})

    app.state.settings = settings

    return app


app = create_app()
