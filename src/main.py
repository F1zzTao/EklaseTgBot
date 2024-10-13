import asyncio
import logging
import sys
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode

from loguru import logger
from config import EKLASE_PASSWORD, EKLASE_USERNAME, TG_BOT_TOKEN
from utils import format_diary, format_homeworks, get_auth_cookies, get_diary, get_raw_diary

dp = Dispatcher()


@dp.message(Command(commands=["расписание", "diary"]))
async def start_handler(message: types.Message):
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

    auth_cookie = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)
    raw_diary: bytes = await get_raw_diary(auth_cookie, today_date)
    diary: list[dict] = get_diary(raw_diary)
    msg += format_diary(diary)

    msg += (
        "Так как я не могу учитывать изменения в расписании, эта информация может быть не точной."
        " Точное расписание может быть в беседе с учителем или в школе."
    )
    await message.answer(msg)


@dp.message(Command(commands=["домашка", "задания", "homework", "exercises"]))
async def homework_handler(message: types.Message):
    today_date = datetime.today()
    week_day_num = today_date.isoweekday()

    is_next_week = False
    if week_day_num >= 5:
        # If it's a day off OR Friday, we skip to the monday
        is_next_week = True
        today_date += timedelta(days=8-week_day_num)

    auth_cookie = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)
    raw_diary: bytes = await get_raw_diary(auth_cookie, today_date)
    diary: list[dict] = get_diary(raw_diary)

    homeworks: list = []
    for day in diary:
        school_day_str = day["date"]
        school_day = datetime.strptime(school_day_str, "%d.%m.%y")
        today_date = datetime.today()
        lessons = []
        for lesson in day["lessons"]:
            if lesson["homework"] is None:
                # If we don't have homework (yay!), we skip the lesson
                continue
            if today_date > school_day:
                # If the homework was in the past, we skip it
                continue

            # Shit, we have homework...
            lessons.append(lesson)
        homeworks.append((school_day, lessons))

    if not homeworks:
        await message.answer(
            f"На {'следующей' if is_next_week else 'этой'} неделе домашек нет. Ура!!"
        )
        return

    msg = format_homeworks(homeworks)
    await message.answer(msg, parse_mode=ParseMode.HTML)


async def main():
    logger.info("Starting bot")
    bot = Bot(TG_BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
