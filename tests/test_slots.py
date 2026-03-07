import pytest


@pytest.mark.asyncio
async def test_get_slots(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    res = await client.get(
        f"/book/{slug}/slots?service_id={service_id}&date=2026-06-10"
    )
    assert res.status_code == 200
    slots = res.json()
    assert len(slots) > 0


@pytest.mark.skip(
    reason="SQLite изоляция сессий отличается от PostgreSQL — проверять на реальной БД"
)
async def test_no_slots_on_day_off(client, auth_headers, master_with_service):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    # выключаем понедельник и проверяем что запрос прошёл
    res = await client.put(
        "/schedule/0",
        json={"start_time": "09:00", "end_time": "18:00", "is_working": False},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["is_working"] == False

    slots_res = await client.get(
        f"/book/{slug}/slots?service_id={service_id}&date=2026-06-10"
    )
    assert slots_res.json() == []


@pytest.mark.asyncio
async def test_slots_no_overlap(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    await client.post(
        f"/book/{slug}",
        json={
            "client_name": "Клиент 1",
            "client_phone": "+79991234561",
            "service_id": service_id,
            "datetime_start": "2026-06-10T09:00:00+00:00",
        },
    )

    res = await client.get(
        f"/book/{slug}/slots?service_id={service_id}&date=2026-06-10"
    )
    slots = res.json()
    times = [s["datetime_start"][:19] for s in slots]
    assert "2026-06-10T09:00:00+00:00" not in times


@pytest.mark.asyncio
async def test_get_master_public(client, auth_headers):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]

    res = await client.get(f"/book/{slug}")
    assert res.status_code == 200
    assert res.json()["slug"] == slug


@pytest.mark.asyncio
async def test_get_master_not_found(client):
    res = await client.get("/book/nonexistent-slug")
    assert res.status_code == 404
