import pytest

@pytest.mark.asyncio
async def test_users_me_success(client):
    # Регистрация и логин
    client.post("/register", data={"username": "meuser", "password": "mepass"})
    login_resp = client.post("/login", data={"username": "meuser", "password": "mepass"})
    token = login_resp.json()["access_token"]
    # Запрос с токеном
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "meuser"

@pytest.mark.asyncio
async def test_users_me_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401 