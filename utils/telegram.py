import httpx
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


async def send_telegram_message(telegram_id: int, text: str):
    """Отправить сообщение мастеру в Telegram."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN не задан, уведомление не отправлено")
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        proxy = settings.PROXY_URL if settings.PROXY_URL else None
        async with httpx.AsyncClient(proxy=proxy, timeout=30.0) as client:
            await client.post(
                url, json={"chat_id": telegram_id, "text": text, "parse_mode": "HTML"}
            )
    except Exception as e:
        logger.error(f"Ошибка отправки Telegram уведомления: {e}", exc_info=True)
