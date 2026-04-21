import httpx
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


async def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Отправить письмо с ссылкой для сброса пароля."""
    payload = {
        "from": "Seansa <noreply@mail.seansa.ru>",
        "to": [to_email],
        "subject": "Восстановление пароля — Seansa",
        "html": f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
            <h2 style="color: #1a1a1a;">Восстановление пароля</h2>
            <p style="color: #6b6560; line-height: 1.6;">
                Вы запросили сброс пароля для вашего аккаунта Seansa.
                Нажмите на кнопку ниже чтобы создать новый пароль.
            </p>
            <a href="{reset_url}" 
               style="display:inline-block;margin:24px 0;padding:14px 28px;
                      background:#c9a84c;color:#fff;text-decoration:none;
                      font-weight:500;border-radius:4px;">
                Сбросить пароль
            </a>
            <p style="color: #9a9080; font-size: 13px;">
                Ссылка действительна 1 час. Если вы не запрашивали сброс пароля — 
                просто проигнорируйте это письмо.
            </p>
        </div>
        """,
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=10.0,
            )
            if res.status_code == 200:
                logger.info(f"Письмо отправлено на {to_email}")
                return True
            else:
                logger.error(f"Ошибка отправки письма: {res.status_code} {res.text}")
                return False
    except Exception as e:
        logger.error(f"Ошибка отправки письма: {e}")
        return False


async def send_new_booking_email(to_email: str, booking_data: dict) -> bool:
    """Отправить письмо мастеру о новой записи."""
    payload = {
        "from": "Seansa <noreply@mail.seansa.ru>",
        "to": [to_email],
        "subject": "Новая запись — Seansa",
        "html": f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
            <h2 style="color: #1a1a1a;">📅 Новая запись!</h2>
            <div style="background:#f7f4f0;border-radius:8px;padding:20px;margin:20px 0;">
                <p style="margin:8px 0;color:#1a1a1a;"><b>Клиент:</b> {booking_data["client_name"]}</p>
                <p style="margin:8px 0;color:#1a1a1a;"><b>Телефон:</b> {booking_data["client_phone"] or "—"}</p>
                <p style="margin:8px 0;color:#1a1a1a;"><b>Соцсеть:</b> {booking_data["client_social"] or "—"}</p>
                <p style="margin:8px 0;color:#1a1a1a;"><b>Услуга:</b> {booking_data["service_name"]}</p>
                <p style="margin:8px 0;color:#1a1a1a;"><b>Дата и время:</b> {booking_data["datetime"]}</p>
            </div>
            <a href="https://seansa.ru/app"
               style="display:inline-block;margin:24px 0;padding:14px 28px;
                      background:#6c63ff;color:#fff;text-decoration:none;
                      font-weight:500;border-radius:4px;">
                Открыть кабинет
            </a>
        </div>
        """,
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=10.0,
            )
            if res.status_code == 200:
                logger.info(f"Письмо о новой записи отправлено на {to_email}")
                return True
            else:
                logger.error(f"Ошибка отправки письма: {res.status_code} {res.text}")
                return False
    except Exception as e:
        logger.error(f"Ошибка отправки письма: {e}")
        return False
