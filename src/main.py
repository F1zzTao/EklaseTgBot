from loguru import logger

from bs4 import BeautifulSoup
from telegrinder import API, Message, Telegrinder, Token
from telegrinder.rules import Text
from datetime import datetime, timedelta

from config import EKLASE_PASSWORD, EKLASE_USERNAME, EMOJIS, TG_BOT_TOKEN
from utils import get_auth_cookies, get_raw_diary

api = API(token=Token(TG_BOT_TOKEN))
bot = Telegrinder(api)


@bot.on.message(Text(["/расписание", "/diary"]))
async def start_handler(message: Message):
    auth_cookie = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)

    today_date = datetime.today()
    week_day = today_date.isoweekday()

    if week_day >= 6:
        # If it's a day off (Saturday or Sunday), we skip to the monday
        today_date += timedelta(days=8-week_day)

    raw_diary = await get_raw_diary(auth_cookie, today_date)

    soup = BeautifulSoup(raw_diary, "html.parser")
    tab_content = soup.find("div", class_="tab-content")

    msg = ""
    days = tab_content.find_all("div", recursive=False)
    for day in days:
        journal_nav = day.find("div", class_="journal-nav")
        date_title = journal_nav.find("h2", class_="mobile-date").getText().strip()
        msg += date_title+':'

        lessons_items = day.find_all("div", class_="actual-lessons-item")

        for lessons_item in lessons_items:
            lesson_number = lessons_item.find("span", class_="number").text.strip()
            if lesson_number == '·':
                continue

            lesson_title = lessons_item.find("span", class_="title").text.strip()
            lesson_room = lessons_item.find("span", class_="room").text.strip()

            lesson_emoji = ""
            for key in EMOJIS:
                if key in lesson_title.lower():
                    lesson_emoji = EMOJIS[key] + " "
                    break

            msg += f"\n{lesson_number} {lesson_emoji}{lesson_title} - {lesson_room}"

        msg += "\n\n"

    await message.answer(msg)


bot.run_forever()
