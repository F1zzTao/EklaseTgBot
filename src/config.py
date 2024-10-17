import os

from dotenv import load_dotenv

load_dotenv()

# Telegram bot token. You can get it from BotFather
TG_BOT_TOKEN: str = os.getenv("TG_BOT_TOKEN")

# Your E-Klase credentials. Set them in `.env` file
EKLASE_USERNAME: str = os.getenv("EKLASE_USERNAME")
EKLASE_PASSWORD: str = os.getenv("EKLASE_PASSWORD")

# SQLite database path
DB_PATH: str = "./db.db"

# Working headers
HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
}

# Different E-Klase URLs that this bot uses
EKLASE_HOME: str = "https://my.e-klase.lv"
EKLASE_LOGIN_URL: str = EKLASE_HOME+"/?v=15"
EKLASE_DIARY_URL: str = EKLASE_HOME+"/Family/Diary"

# Boring emojis for homework
BORING_EMOJIS: tuple[str] = ('🥱', '🙄', '😮‍💨', '😩', '😴', '😒', '😭', '💀', '💔')

# Emojis based on lesson amount
FEW_LESSONS_EMOJIS: tuple[str] = ('😮‍💨', '🎉', '🤩')
OKAY_LESSONS_EMOJIS: tuple[str] = ('😅', '🤨', '😐')
MUCH_LESSONS_EMOJIS: tuple[str] = ('😭', '😨', '💀')

FEW_LESSONS_MIN_COUNT: int = 1
OKAY_LESSONS_MIN_COUNT: int = 7
MUCH_LESSONS_MIN_COUNT: int = 8

# Information about lessons. Each lesson must be a part of its name and it
# must have an emoji and translation
LESSONS_INFO: dict = {
    "ģeogrāfija": {"emoji": "🌍", "translation": "География"},
    "svešvaloda i (b2)": {"emoji": "🇬🇧", "translation": "Английский язык (B2)"},
    "svešvaloda (b1)": {"emoji": "🇩🇪", "translation": "Немецкий язык (B1)"},
    "matemātika": {"emoji": "➗", "translation": "Математика"},
    "bioloģija": {"emoji": "🧬", "translation": "Биология"},
    "mazākumtautības": {"emoji": "🇷🇺", "translation": "Русский язык"},
    "literatūra": {"emoji": "📝", "translation": "Литература"},  # this must be below russian
    "latviešu": {"emoji": "🇱🇻", "translation": "Латышский язык"},
    "ekonomika": {"emoji": "💰", "translation": "Экономика"},
    "sports": {"emoji": "🏃‍♂️", "translation": "Спорт"},
    "fizika": {"emoji": "⚛️", "translation": "Физика"},
    "ķīmija": {"emoji": "🧪", "translation": "Химия"},
    "vēsture": {"emoji": "📜", "translation": "История"},
    "sociālās": {"emoji": "🌍", "translation": "Соц. знания"},
    "programmēšana": {"emoji": "💻", "translation": "Программирование"},
    "klases": {"emoji": "🏫", "translation": "Классный час"}
}
SPORT_ROOM_TRANSLATION: str = "сз."

# Week days translations
WEEK_DAY_INFO: dict = {
    "pirmdiena": {"translation": "Понедельник"},
    "otrdiena": {"translation": "Вторник"},
    "trešdiena": {"translation": "Среда"},
    "ceturtdiena": {"translation": "Четверг"},
    "piektdiena": {"translation": "Пятница"},
}

# Close days translation (yesterday, today, etc.)
CLOSE_DAY_INFO: dict = {
    "aizvakar": {"translation": "позавчера"},
    "vakar": {"translation": "вчера"},
    "šodien": {"translation": "сегодня"},
    "rīt": {"translation": "завтра"},
    "parīt": {"translation": "послезавтра"},
}

# Lesson length
NORMAL_LESSON_TIME: int = 40 * 60  # 40 minutes
SHORT_LESSON_TIME: int = 30 * 60   # 30 minutes

# Timetables. They must contain lesson's start time
NORMAL_LESSON_TIMETABLE: dict = {
    1: "8:10",
    2: "9:00",
    3: "9:55",
    4: "10:50",
    5: "11:45",
    6: "12:40",
    7: "13:30",
    8: "14:15",
    9: "15:00"
}
SHORT_LESSON_TIMETABLE: dict = {
    1: "8:10",
    2: "8:50",
    3: "9:35",
    4: "10:20",
    5: "11:05",
    6: "12:40",
    7: "13:30",
    8: "14:15",
    9: "15:00"
}
