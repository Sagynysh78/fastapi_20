import pytest

@pytest.mark.asyncio
async def test_register_success(client):
    response = client.post("/register", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["message"] == "User registered"

@pytest.mark.asyncio
async def test_register_duplicate(client):
    client.post("/register", data={"username": "dupuser", "password": "pass1"})
    response = client.post("/register", data={"username": "dupuser", "password": "pass2"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

@pytest.mark.asyncio
async def test_login_success(client):
    client.post("/register", data={"username": "loginuser", "password": "loginpass"})
    response = client.post("/login", data={"username": "loginuser", "password": "loginpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_data(client):
    client.post("/register", data={"username": "wronguser", "password": "rightpass"})
    response = client.post("/login", data={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password" 