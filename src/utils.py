import asyncio
import re
from datetime import datetime
from http.cookies import SimpleCookie

import aiohttp
from aiocache import cached
from bs4 import BeautifulSoup
from loguru import logger

from config import (
    CLOSE_DAY_INFO,
    EKLASE_DIARY_URL,
    EKLASE_HOME,
    EKLASE_LOGIN_URL,
    EKLASE_PASSWORD,
    EKLASE_USERNAME,
    HEADERS,
    LESSONS_INFO,
    SPORT_ROOM_TRANSLATION,
    WEEK_DAY_INFO
)


@cached(ttl=30)
async def get_auth_cookies(username: str, password: str):
    logger.info(f"Getting auth cookies of this user: {username}")
    login_data = {
        'UserName': username,
        'Password': password,
    }
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # Login
        logger.debug(f"First url: {EKLASE_LOGIN_URL}")
        async with session.post(
            EKLASE_LOGIN_URL, data=login_data, allow_redirects=False
        ) as r_login:
            redirect_url = EKLASE_HOME + r_login.headers['Location']
            logger.debug(f"Redirect url: {redirect_url}")

        # First redirect
        async with session.get(
            redirect_url, cookies=r_login.cookies, allow_redirects=False
        ) as r_login_1:
            redirect_url = EKLASE_HOME + r_login_1.headers['Location']
            logger.debug(f"Next redirect url: {redirect_url}")

        # Second redirect
        async with session.get(
            redirect_url, cookies=r_login.cookies, allow_redirects=False
        ) as r_login_2:
            content = await r_login_2.read()
            text = content.decode("utf-8")

            # Extracting TenantId and pf_id
            tenant_id_pattern = re.search(r"name='TenantId' value='(.*?)'", text)
            pf_id_pattern = re.search(r"name='pf_id' value='(.*?)'", text)

            tenant_id = tenant_id_pattern.group(1) if tenant_id_pattern else None
            pf_id = pf_id_pattern.group(1) if pf_id_pattern else None

            logger.debug(f"TenantId: {tenant_id}")
            logger.debug(f"pf_id: {pf_id}")

            login_datas = {
                "TenantId": tenant_id,
                "pf_id": pf_id
            }

            # Another redirect, through <form> now
            redirect_url_pattern = re.search(r"^<form action='(.*?)'", text)
            redirect_url = EKLASE_HOME + redirect_url_pattern.group(1)
            logger.debug(f"Next redirect url: {redirect_url}")

        # Final form submission
        async with session.post(
            redirect_url,
            data=login_datas,
            cookies=r_login.cookies,
            allow_redirects=False,
        ) as r_login_final:
            return r_login_final.cookies


@cached(ttl=30)
async def get_raw_diary(
    cookie: SimpleCookie, date: datetime | None = None
) -> bytes:
    if not date:
        date = datetime.today()

    diary_url = EKLASE_DIARY_URL+f"?Date={date.day}.{date.month}.{date.year}"
    logger.info(f"Diary from {date}: {diary_url}")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(diary_url, cookies=cookie) as r_diary:
            return (await r_diary.read())


def get_diary(raw_diary: bytes) -> list[dict]:
    soup = BeautifulSoup(raw_diary, "html.parser")
    tab_content = soup.find("div", class_="tab-content")

    days = tab_content.find_all("div", recursive=False)
    days_list = []
    for day in days:
        this_day_dict = {
            "date": None,
            "week_day": None,
            "close_day": None,
            "lessons": []
        }
        journal_nav = day.find("div", class_="journal-nav")
        date_title = journal_nav.find("h2", class_="mobile-date").getText().strip()
        date_splitted = date_title.split()
        date_str, week_day = date_splitted[0].rstrip('.'), date_splitted[1]
        close_day = None
        if len(date_splitted) >= 3:
            close_day = date_splitted[2].replace('(', '').replace(')', '')

        this_day_dict['date'] = date_str
        this_day_dict['week_day'] = week_day
        this_day_dict['close_day'] = close_day

        lessons_items = day.find_all("div", class_="actual-lessons-item")

        for lessons_item in lessons_items:
            this_lesson_dict = {
                "num": None,
                "name": None,
                "topic": None,
                "homework": None,
                "cab": None,
            }
            lesson_number = lessons_item.find("span", class_="number").text.strip()
            if lesson_number == '·':
                continue

            lesson_title = lessons_item.find("span", class_="title").text.strip()
            lesson_room = lessons_item.find("span", class_="room").text.strip()

            # Extracting topic
            lesson_topic_div = lessons_item.find("div", class_="lesson-subitem subject")
            lesson_topic = ""
            if lesson_topic_div:
                lesson_topics = lesson_topic_div.find_all("p")
                for topic in lesson_topics:
                    # Converting the text and tags into a string
                    lesson_topic += ''.join(
                        str(child) for child in topic.children
                    ).strip() + "\n"
                for file in lesson_topic_div.find_all("a", class_="file", href=True):
                    href_link = EKLASE_HOME+file["href"]
                    lesson_topic += f'<a href="{href_link}">{file.text}</a>\n'
                lesson_topic = lesson_topic.strip()
            if not lesson_topic:
                lesson_topic = None

            # Extracting homework
            lesson_homework_divs = lessons_item.find_all('div', class_='lesson-subitem')
            lesson_homework_div = lesson_homework_divs[-1]
            lesson_homework_description = lesson_homework_div.find('div', class_='description')
            lesson_homework = ""
            if lesson_homework_description:
                lesson_homeworks = lesson_homework_description.find_all("p")
                for homework in lesson_homeworks:
                    # Converting the text and tags into a string
                    lesson_homework += ''.join(
                        str(child) for child in homework.children
                    ).strip() + "\n"
                for file in lesson_homework_description.find_all("a", class_="file", href=True):
                    href_link = EKLASE_HOME+file["href"]
                    lesson_homework += f'<a href="{href_link}">{file.text}</a> '
                lesson_homework = lesson_homework.strip()
            if not lesson_homework:
                lesson_homework = None

            this_lesson_dict['num'] = lesson_number
            this_lesson_dict['name'] = lesson_title
            this_lesson_dict['topic'] = lesson_topic
            this_lesson_dict['homework'] = lesson_homework
            this_lesson_dict['cab'] = lesson_room

            this_day_dict['lessons'].append(this_lesson_dict)
        days_list.append(this_day_dict)

    logger.debug(f"Diary: {days_list}")
    return days_list


def format_diary(diary: list[dict]) -> str:
    msg = ""
    for day in diary:
        week_day = find_t(day['week_day'], WEEK_DAY_INFO) or day['week_day']
        close_day = day['close_day']
        if close_day:
            close_day = find_t(close_day, CLOSE_DAY_INFO, exact=True) or close_day
        date_str = day['date']
        msg += f"{week_day} {'('+close_day+') ' if close_day else ''} - {date_str}:"

        for lesson in day['lessons']:
            lesson_num = lesson['num']
            lesson_title = find_t(lesson['name'], LESSONS_INFO) or lesson['name']
            lesson_room = SPORT_ROOM_TRANSLATION if lesson['cab'] == "sz" else lesson['cab']
            lesson_emoji = None
            for key in LESSONS_INFO:
                if key in lesson['name'].lower():
                    lesson_emoji = LESSONS_INFO[key]['emoji'] + " "
                    break
            msg += f"\n{lesson_num} {lesson_emoji}{lesson_title} - {lesson_room}"
        msg += "\n\n"
    return msg


def format_homeworks(homeworks: list[tuple[datetime, list[dict]]]) -> str:
    msg = ""
    for date, lessons in homeworks:
        msg += f"{date.strftime('%d.%m.%y')}:"
        for lesson in lessons:
            lesson_title = find_t(lesson['name'], LESSONS_INFO) or lesson['name']
            lesson_homework = lesson['homework']
            lesson_emoji = None
            for key in LESSONS_INFO:
                if key in lesson['name'].lower():
                    lesson_emoji = LESSONS_INFO[key]['emoji'] + " "
                    break
            msg += f"\n- {lesson_emoji}{lesson_title} - {lesson_homework}"
        msg += "\n\n"
    return msg


def find_t(string: str | None, translations: dict, exact: bool = False):
    if string is None:
        return

    for key in translations:
        if exact:
            if key == string.lower():
                return translations[key]['translation']
        else:
            if key in string.lower():
                return translations[key]['translation']


async def main():
    cookies = await get_auth_cookies(EKLASE_USERNAME, EKLASE_PASSWORD)
    raw_diary = await get_raw_diary(cookies)
    with open("eklase_diary.html", "wb") as f:
        f.write(raw_diary)

    diary = get_diary(raw_diary)
    logger.info(diary)


if __name__ == "__main__":
    asyncio.run(main())
