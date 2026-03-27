import pytest


@pytest.mark.asyncio
async def test_register_success(client, master_data):
    res = await client.post("/auth/register", json=master_data)
    assert res.status_code == 200
    data = res.json()
    assert data["phone"] == master_data["phone"]
    assert data["name"] == master_data["name"]


@pytest.mark.asyncio
async def test_register_duplicate_phone(client, master_data, registered_master):
    res = await client.post("/auth/register", json=master_data)
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client, master_data, registered_master):
    res = await client.post(
        "/auth/login",
        json={"phone": master_data["phone"], "password": master_data["password"]},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client, master_data, registered_master):
    res = await client.post(
        "/auth/login", json={"phone": master_data["phone"], "password": "wrongpassword"}
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_phone(client, master_data):
    res = await client.post(
        "/auth/login",
        json={"phone": "+79990000000", "password": master_data["password"]},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(client, auth_headers, master_data):
    res = await client.get("/master/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["phone"] == master_data["phone"]


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client):
    res = await client.get("/master/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client, registered_master, master_data):
    login_res = await client.post(
        "/auth/login",
        json={"phone": master_data["phone"], "password": master_data["password"]},
    )
    refresh_token = login_res.json()["refresh_token"]
    res = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_register_invalid_phone_no_plus(client):
    res = await client.post(
        "/auth/register",
        json={"name": "Тест", "phone": "9525447085", "password": "password123"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_phone_format(client):
    res = await client.post(
        "/auth/register",
        json={"name": "Тест", "phone": "abc123", "password": "password123"},
    )
    assert res.status_code == 422
