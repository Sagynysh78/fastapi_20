import pytest

@pytest.mark.asyncio
def register_and_login(client, username, password):
    client.post("/register", data={"username": username, "password": password})
    resp = client.post("/login", data={"username": username, "password": password})
    return resp.json()["access_token"]

@pytest.mark.asyncio
async def test_create_note(client):
    token = register_and_login(client, "noteuser", "notepass")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/notes/", json={"text": "Test note"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["text"] == "Test note"

@pytest.mark.asyncio
async def test_get_notes_only_own(client):
    token1 = register_and_login(client, "user1", "pass1")
    token2 = register_and_login(client, "user2", "pass2")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    # user1 создает заметку
    client.post("/notes/", json={"text": "Note1"}, headers=headers1)
    # user2 создает заметку
    client.post("/notes/", json={"text": "Note2"}, headers=headers2)
    # user1 получает только свою
    resp1 = client.get("/notes/", headers=headers1)
    assert resp1.status_code == 200
    notes1 = resp1.json()
    assert any(note["text"] == "Note1" for note in notes1)
    assert all(note["text"] != "Note2" for note in notes1)
    # user2 получает только свою
    resp2 = client.get("/notes/", headers=headers2)
    assert resp2.status_code == 200
    notes2 = resp2.json()
    assert any(note["text"] == "Note2" for note in notes2)
    assert all(note["text"] != "Note1" for note in notes2)

@pytest.mark.asyncio
async def test_delete_own_and_foreign_note(client):
    token1 = register_and_login(client, "deluser1", "delpass1")
    token2 = register_and_login(client, "deluser2", "delpass2")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    # user1 создает заметку
    resp = client.post("/notes/", json={"text": "Delete me"}, headers=headers1)
    note_id = resp.json()["id"]
    # user2 пытается удалить чужую
    resp_forbidden = client.delete(f"/notes/{note_id}", headers=headers2)
    assert resp_forbidden.status_code == 404
    # user1 удаляет свою
    resp_ok = client.delete(f"/notes/{note_id}", headers=headers1)
    assert resp_ok.status_code == 200
    assert resp_ok.json()["ok"] is True 