import asyncio
import logging
import sys
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from loguru import logger
from config import EKLASE_PASSWORD, EKLASE_USERNAME, TG_BOT_TOKEN
from utils import format_diary, get_auth_cookies, get_diary, get_raw_diary

dp = Dispatcher()


@dp.message(Command(commands=["расписание", "diary"]))
async def start_handler(message: types.Message):
    auth_cookie = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)

    msg = ""
    today_date = datetime.today()
    week_day_num = today_date.isoweekday()

    if week_day_num >= 6:
        # If it's a day off (Saturday or Sunday), we skip to the monday
        today_date += timedelta(days=8-week_day_num)
        msg = "🗓️ Расписание на следующую неделю:"
    else:
        msg = "📅 Расписание на эту неделю:"
    msg += "\n\n"

    raw_diary: bytes = await get_raw_diary(auth_cookie, today_date)

    diary: list[dict] = get_diary(raw_diary)
    msg += format_diary(diary)

    msg += (
        "Так как я не могу учитывать изменения в расписании, эта информация может быть не точной."
        " Точное расписание может быть в беседе с учителем или в школе."
    )
    await message.answer(msg)


async def main():
    logger.info("Starting bot")
    bot = Bot(TG_BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
