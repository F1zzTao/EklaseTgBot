from http.cookies import SimpleCookie
from loguru import logger
import re

import aiohttp
from datetime import datetime

from config import EKLASE_DIARY_URL, EKLASE_HOME, EKLASE_LOGIN_URL, HEADERS


async def get_auth_cookies(username: str, password: str):
    logger.info("Getting auth cookies from e-klase...")
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


async def get_raw_diary(cookie: SimpleCookie, date: datetime | None) -> bytes:
    if not date:
        date = datetime.today()

    diary_url = EKLASE_DIARY_URL+f"?Date={date.day}.{date.month}.{date.year}"
    logger.info(f"Getting diary from this url: {diary_url}")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(diary_url, cookies=cookie) as r_diary:
            return (await r_diary.read())
