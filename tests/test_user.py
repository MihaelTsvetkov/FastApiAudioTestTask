import pytest
from httpx import AsyncClient
from models.user import User


@pytest.mark.asyncio
async def test_read_me_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_me_authorized(
    client: AsyncClient,
    user_token: str,
    test_user: User
) -> None:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await client.get("/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email
