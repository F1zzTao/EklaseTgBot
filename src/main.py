import asyncio
import logging
import random
import sys
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from loguru import logger

from config import (
    BORING_EMOJIS,
    EKLASE_PASSWORD,
    EKLASE_USERNAME,
    FEW_LESSONS_EMOJIS,
    MUCH_LESSONS_EMOJIS,
    MUCH_LESSONS_MIN_COUNT,
    NORMAL_LESSON_TIMETABLE,
    OKAY_LESSONS_EMOJIS,
    OKAY_LESSONS_MIN_COUNT,
    TG_BOT_TOKEN
)
from db import create_tables
from utils import (
    format_diary,
    format_list_lessons,
    get_auth_cookies,
    get_diary,
    get_raw_diary,
    get_today_diary
)

dp = Dispatcher()


@dp.message(Command(commands=["расписание", "diary"]))
async def start_handler(message: types.Message):
    """
    Returns this or next week's diary, depending on which day is today.
    """
    msg: str = ""
    today_date = datetime.today().date()
    week_day_num: int = today_date.isoweekday()

    if week_day_num >= 6:
        # If it's a day off (Saturday or Sunday), we skip to the monday
        today_date += timedelta(days=8-week_day_num)
        msg = "🗓️ Расписание на следующую неделю:"
    else:
        msg = "📅 Расписание на эту неделю:"
    msg += "\n\n"

    # Logging into e-klase and getting diary HTML page
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
    """
    Returns this or next week's homework, depending on which day is today.
    """
    today_date = datetime.today().date()
    week_day_num: int = today_date.isoweekday()

    is_next_week: bool = False
    if week_day_num >= 6:
        # If it's a day off (Saturday or Sunday), we skip to the monday
        is_next_week = True
        today_date += timedelta(days=8-week_day_num)

    # Logging into e-klase and getting diary HTML page
    auth_cookie = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)
    raw_diary: bytes = await get_raw_diary(auth_cookie, today_date)

    diary: list[dict] = get_diary(raw_diary)

    skipped_past: bool = False
    homeworks: list = []
    for day in diary:
        school_day_str = day["date"]
        school_day = datetime.strptime(school_day_str, "%d.%m.%y").date()
        lessons = []
        for lesson in day["lessons"]:
            if lesson["homework"] is None:
                # If we don't have homework (yay!), we skip the lesson
                continue
            if today_date > school_day:
                # If the homework was in the past, we skip it
                skipped_past = True
                continue

            # Shit, we have homework...
            lessons.append(lesson)
        homeworks.append((school_day, lessons))

    if not homeworks:
        await message.answer(
            f"🎉 На {'следующей' if is_next_week else 'этой'} неделе домашек нет. Ура!!"
        )
        return

    homework_count: int = sum(len(item[1]) for item in homeworks)

    if homework_count >= 2 and skipped_past:
        left_msg = "осталось"
    elif homework_count <= 1 and skipped_past:
        left_msg = "осталась"
    else:
        left_msg = "есть"

    # Random boring emojis, because we hate homeworks
    emoji: str = random.choice(BORING_EMOJIS)

    msg: str = (
        f"{emoji} На {'следующей' if is_next_week else 'этой'} неделе"
        f" {left_msg}"
        f" {'аж '+str(homework_count)+' домашек...' if homework_count >= 2 else '1 домашка:'}\n\n"
    )
    msg += format_list_lessons(homeworks, show_num=False)
    await message.answer(
        msg,
        link_preview_options=types.LinkPreviewOptions(is_disabled=True)
    )


@dp.message(Command(commands=["звонки", "bells", "school", "today"]))
async def bells_handler(message: types.Message):
    """
    Returns today's diary together with lesson's start time.
    Also bolds the next lesson.
    """
    today_date = datetime.today().date()
    week_day_num: int = today_date.isoweekday()

    if week_day_num >= 6:
        # If it's a day off (Saturday or Sunday), we skip to the monday
        today_date += timedelta(days=8-week_day_num)

    # Logging into e-klase and getting diary HTML page
    auth_cookie = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)
    raw_diary: bytes = await get_raw_diary(auth_cookie, today_date)

    diary: list[dict] = get_diary(raw_diary)
    today_diary: dict | None = get_today_diary(diary, today_date)

    if not today_diary:
        msg = f"{FEW_LESSONS_EMOJIS} Сегодня выходной!"
        await message.answer(msg)

    lesson_count: int = len(today_diary['lessons'])
    ending: str = ''
    if lesson_count >= 3:
        ending = 'ов'
    elif lesson_count >= 2:
        ending = 'а'

    # Different emojis based on lesson amount
    if lesson_count >= MUCH_LESSONS_MIN_COUNT:
        emojis = MUCH_LESSONS_EMOJIS
    elif lesson_count >= OKAY_LESSONS_MIN_COUNT:
        emojis = OKAY_LESSONS_EMOJIS
    else:
        emojis = FEW_LESSONS_EMOJIS
    lesson_emoji: str = random.choice(emojis)

    msg: str = f"{lesson_emoji} Сегодня всего {lesson_count} урок{ending}.\n\n"
    msg += format_list_lessons(
        [(today_date, today_diary["lessons"],)],
        add_time=True,
        timetable=NORMAL_LESSON_TIMETABLE,
        add_homework=False,
        add_homework_notif=True,
        show_next_lesson=True,
    )
    await message.answer(msg)


async def main():
    # Creating bot instance and creating SQL tables
    bot = Bot(TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(create_tables)

    logger.info("Starting bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
