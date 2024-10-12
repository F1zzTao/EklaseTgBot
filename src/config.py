import os

from dotenv import load_dotenv

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

EKLASE_USERNAME = os.getenv("EKLASE_USERNAME")
EKLASE_PASSWORD = os.getenv("EKLASE_PASSWORD")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
}
EKLASE_HOME = "https://my.e-klase.lv"
EKLASE_LOGIN_URL = EKLASE_HOME+"/?v=15"
EKLASE_DIARY_URL = EKLASE_HOME+"/Family/Diary"

EMOJIS = {
    "ģeogrāfija": "🌍",
    "svešvaloda i (b2)": "🇬🇧",  # English
    "svešvaloda (b1)": "🇩🇪",    # German
    "matemātika": "➗",
    "bioloģija": "🧬",
    "literatūra": "📝",
    "latviešu": "🇱🇻",           # Latvian
    "ekonomika": "💰",
    "sports": "🏃‍♂️",
    "fizika": "⚛️",
    "ķīmija": "🧪",
    "vēsture": "📜",
    "sociālās": "🌍",
    "programmēšana": "💻",
    "mazākumtautības": "🇷🇺",    # Russian
    "klases": "🏫"
}
