import pytest
from unittest.mock import patch, AsyncMock


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


@pytest.mark.asyncio
async def test_booking_sends_telegram_notification(
    client, auth_headers, master_with_service, master_with_schedule
):
    # Устанавливаем telegram_id мастеру
    await client.put(
        "/master/me",
        json={"telegram_id": 123456789},
        headers=auth_headers,
    )

    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    with patch("api.public.send_telegram_message", new_callable=AsyncMock) as mock_tg:
        booking_res = await client.post(
            f"/book/{slug}",
            json={
                "client_name": "Тест Клиент",
                "client_phone": "+79991234568",
                "service_id": service_id,
                "datetime_start": "2026-06-10T11:00:00+00:00",
            },
        )
        assert booking_res.status_code == 200
        mock_tg.assert_called_once()
        call_args = mock_tg.call_args
        assert call_args[0][0] == 123456789  # правильный telegram_id
        assert "Тест Клиент" in call_args[0][1]  # имя клиента в тексте


@pytest.mark.asyncio
async def test_booking_no_telegram_if_not_set(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    with patch("api.public.send_telegram_message", new_callable=AsyncMock) as mock_tg:
        booking_res = await client.post(
            f"/book/{slug}",
            json={
                "client_name": "Тест Клиент",
                "client_phone": "+79991234568",
                "service_id": service_id,
                "datetime_start": "2026-06-10T12:00:00+00:00",
            },
        )
        assert booking_res.status_code == 200
        mock_tg.assert_not_called()  # уведомление не отправлялось


@pytest.mark.asyncio
async def test_booking_without_phone(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    res = await client.post(
        f"/book/{slug}",
        json={
            "client_name": "Тест Клиент",
            "service_id": service_id,
            "datetime_start": "2026-06-10T13:00:00+00:00",
        },
    )
    assert res.status_code == 200
    assert res.json()["client_name"] == "Тест Клиент"


@pytest.mark.asyncio
async def test_booking_with_social(
    client, auth_headers, master_with_service, master_with_schedule
):
    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    res = await client.post(
        f"/book/{slug}",
        json={
            "client_name": "Тест Клиент",
            "client_phone": "+79991234567",
            "client_social": "https://t.me/testuser",
            "service_id": service_id,
            "datetime_start": "2026-06-10T14:00:00+00:00",
        },
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_booking_sends_email_notification(
    client, auth_headers, master_with_service, master_with_schedule
):
    await client.put(
        "/master/me",
        json={"email": "master@test.com", "notify_email": True},
        headers=auth_headers,
    )

    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    with patch(
        "api.public.send_new_booking_email", new_callable=AsyncMock
    ) as mock_email:
        booking_res = await client.post(
            f"/book/{slug}",
            json={
                "client_name": "Тест Клиент",
                "client_phone": "+79991234568",
                "service_id": service_id,
                "datetime_start": "2026-06-11T09:00:00+00:00",
            },
        )
        assert booking_res.status_code == 200
        mock_email.assert_called_once()


@pytest.mark.asyncio
async def test_booking_no_email_if_disabled(
    client, auth_headers, master_with_service, master_with_schedule
):
    await client.put(
        "/master/me",
        json={"email": "master@test.com", "notify_email": False},
        headers=auth_headers,
    )

    master_res = await client.get("/master/me", headers=auth_headers)
    slug = master_res.json()["slug"]
    service_id = master_with_service["id"]

    with patch(
        "api.public.send_new_booking_email", new_callable=AsyncMock
    ) as mock_email:
        booking_res = await client.post(
            f"/book/{slug}",
            json={
                "client_name": "Тест Клиент",
                "client_phone": "+79991234568",
                "service_id": service_id,
                "datetime_start": "2026-06-11T10:00:00+00:00",
            },
        )
        assert booking_res.status_code == 200
        mock_email.assert_not_called()
