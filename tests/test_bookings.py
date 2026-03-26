import pytest


@pytest.mark.asyncio
async def test_create_service(client, auth_headers):
    res = await client.post(
        "/services/",
        json={"name": "Стрижка", "duration": 30, "price": 500},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Стрижка"


@pytest.mark.asyncio
async def test_get_services(client, auth_headers, master_with_service):
    res = await client.get("/services/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


@pytest.mark.asyncio
async def test_delete_service(client, auth_headers, master_with_service):
    service_id = master_with_service["id"]
    res = await client.delete(f"/services/{service_id}", headers=auth_headers)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_bookings_empty(client, auth_headers):
    res = await client.get("/bookings/", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_update_booking_status(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    booking_res = await client.post(
        f"/book/{slug}",
        json={
            "client_name": "Тест Клиент",
            "client_phone": "+79991234568",
            "service_id": service_id,
            "datetime_start": "2026-06-10T09:00:00+00:00",
        },
    )
    assert booking_res.status_code == 200
    booking_id = booking_res.json()["id"]

    res = await client.patch(
        f"/bookings/{booking_id}/status",
        json={"status": "confirmed"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_cancel_booking_by_token(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    booking_res = await client.post(
        f"/book/{slug}",
        json={
            "client_name": "Тест Клиент",
            "client_phone": "+79991234568",
            "service_id": service_id,
            "datetime_start": "2026-06-10T10:00:00+00:00",
        },
    )
    cancel_token = booking_res.json()["cancel_token"]

    res = await client.get(f"/cancel/{cancel_token}")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_update_booking_notes(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    booking_res = await client.post(
        f"/book/{slug}",
        json={
            "client_name": "Тест Клиент",
            "client_phone": "+79991234568",
            "service_id": service_id,
            "datetime_start": "2026-06-10T09:00:00+00:00",
        },
    )
    assert booking_res.status_code == 200
    booking_id = booking_res.json()["id"]

    res = await client.patch(
        f"/bookings/{booking_id}/notes",
        json={"notes": "Аллергия на гель"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["notes"] == "Аллергия на гель"

    res = await client.patch(
        f"/bookings/{booking_id}/notes",
        json={"notes": None},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["notes"] is None
