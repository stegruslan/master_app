import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector
from core.config import settings


dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"👋 Привет!\n\n"
        f"Ваш Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"Скопируйте его и вставьте в настройках аккаунта на seansa.ru",
        parse_mode="HTML",
    )


async def main():
    connector = ProxyConnector.from_url(settings.PROXY_URL)
    session = AiohttpSession(connector=connector)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
