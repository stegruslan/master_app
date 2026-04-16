import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from core.config import settings


bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
db = Dispatcher()


@db.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"👋 Привет!\n\n"
        f"Ваш Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"Скопируйте его и вставьте в настройках аккаунта на seansa.ru",
        parse_mode="HTML",
    )


async def main():
    await db.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
