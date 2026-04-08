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


@pytest.mark.asyncio
async def test_forgot_password_success(client, registered_master):
    res = await client.post(
        "/auth/forgot-password",
        json={"email": registered_master["email"]},
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password_unknown_email(client):
    res = await client.post(
        "/auth/forgot-password",
        json={"email": "notexist@example.com"},
    )
    # Возвращаем 200 чтобы не раскрывать существование аккаунта
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_success(client, registered_master, db_session):
    from models.password_reset import PasswordResetToken
    from datetime import datetime, timezone, timedelta
    import secrets

    token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        master_id=registered_master["id"],
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        used=False,
    )
    db_session.add(reset_token)
    await db_session.commit()

    res = await client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "newpassword123"},
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    res = await client.post(
        "/auth/reset-password",
        json={"token": "invalidtoken", "new_password": "newpassword123"},
    )
    assert res.status_code == 400
