import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_users_no_auth(client: AsyncClient) -> None:
    response = await client.get("/admin/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_not_superuser(
    client: AsyncClient,
    user_token: str
) -> None:
    response = await client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_users_superuser(
    client: AsyncClient,
    superuser_token: str,
    superuser
) -> None:
    response = await client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    emails = [item["email"] for item in data]
    assert superuser.email in emails


@pytest.mark.asyncio
async def test_delete_user(
    client: AsyncClient,
    superuser_token: str,
    test_user
) -> None:
    response = await client.delete(
        f"/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == 200

    response = await client.delete(
        f"/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == 204
