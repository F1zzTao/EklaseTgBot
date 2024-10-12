from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from loguru import logger
from telegrinder import API, Message, Telegrinder, Token
from telegrinder.rules import Text

from config import (
    CLOSE_DATE_INFO,
    EKLASE_PASSWORD,
    EKLASE_USERNAME,
    LESSONS_INFO,
    SPORT_ROOM_TRANSLATION,
    TG_BOT_TOKEN,
    WEEK_DAY_INFO
)
from utils import get_auth_cookies, get_raw_diary

api = API(token=Token(TG_BOT_TOKEN))
bot = Telegrinder(api)


@bot.on.message(Text(["/расписание", "/diary"]))
async def start_handler(message: Message):
    logger.info(f"Getting auth cookies of this user: {EKLASE_USERNAME}")
    auth_cookie = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)

    msg = ""
    today_date = datetime.today()
    week_day = today_date.isoweekday()

    if week_day >= 6:
        # If it's a day off (Saturday or Sunday), we skip to the monday
        today_date += timedelta(days=8-week_day)
        msg = "🗓️ Расписание на следующую неделю:"
    else:
        msg = "📅 Расписание на эту неделю:"
    msg += "\n\n"

    logger.info(f"Getting diary of {EKLASE_USERNAME} from this date: {today_date}")
    raw_diary = await get_raw_diary(auth_cookie, today_date)

    soup = BeautifulSoup(raw_diary, "html.parser")
    tab_content = soup.find("div", class_="tab-content")

    days = tab_content.find_all("div", recursive=False)
    for day in days:
        journal_nav = day.find("div", class_="journal-nav")
        date_title = journal_nav.find("h2", class_="mobile-date").getText().strip()
        date_splitted = date_title.split()
        date_str, week_day = date_splitted[0].rstrip('.'), date_splitted[1]
        close_day = None
        if len(date_splitted) >= 3:
            close_day = date_splitted[2].replace('(', '').replace(')', '')

        for key in WEEK_DAY_INFO:
            if key in week_day.lower():
                week_day = WEEK_DAY_INFO[key].capitalize()
                break
        if close_day:
            for key in CLOSE_DATE_INFO:
                if key in close_day.lower():
                    close_day = CLOSE_DATE_INFO[key]
                    break

        msg += f"{week_day} {'('+close_day+') ' if close_day else ''} - {date_str}:"

        lessons_items = day.find_all("div", class_="actual-lessons-item")

        for lessons_item in lessons_items:
            lesson_number = lessons_item.find("span", class_="number").text.strip()
            if lesson_number == '·':
                continue

            lesson_title = lessons_item.find("span", class_="title").text.strip()
            lesson_room = lessons_item.find("span", class_="room").text.strip()
            if lesson_room == "sz.":
                # Sporta zāle translation
                lesson_room = SPORT_ROOM_TRANSLATION

            lesson_emoji = ""
            for key in LESSONS_INFO:
                if key in lesson_title.lower():
                    lesson_emoji = LESSONS_INFO[key]['emoji'] + " "
                    lesson_title = LESSONS_INFO[key]['translation']
                    break

            msg += f"\n{lesson_number} {lesson_emoji}{lesson_title} - {lesson_room}"

        msg += "\n\n"

    msg += (
        "Так как я не могу учитывать изменения в расписании, эта информация может быть не точной."
        " Точное расписание может быть в беседе с учителем или в школе."
    )
    await message.answer(msg)


bot.run_forever()
