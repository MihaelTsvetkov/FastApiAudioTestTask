import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_files_empty(
    client: AsyncClient,
    user_token: str
) -> None:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await client.get("/files", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_upload_audio_file(
    client: AsyncClient,
    user_token: str
) -> None:
    headers = {"Authorization": f"Bearer {user_token}"}
    fake_file_data = io.BytesIO(b"fake-audio-data")

    files = {
        "file": ("test_audio.mp3", fake_file_data, "audio/mpeg")
    }
    data = {
        "filename": "my_test_file"
    }

    response = await client.post(
        "/files/upload",
        headers=headers,
        data=data,
        files=files
    )
    assert response.status_code == 201
    resp_data = response.json()
    assert resp_data["filename"] == "my_test_file"
    assert "id" in resp_data


@pytest.mark.asyncio
async def test_get_user_files_after_upload(
    client: AsyncClient,
    user_token: str,
    uploaded_file: str
) -> None:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await client.get("/files", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
