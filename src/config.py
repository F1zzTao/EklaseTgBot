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

LESSONS_INFO = {
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
SPORT_ROOM_TRANSLATION = "сз."
WEEK_DAY_INFO = {
    "pirmdiena": {"translation": "Понедельник"},
    "otrdiena": {"translation": "Вторник"},
    "trešdiena": {"translation": "Среда"},
    "ceturtdiena": {"translation": "Четверг"},
    "piektdiena": {"translation": "Пятница"},
}
CLOSE_DAY_INFO = {
    "aizvakar": {"translation": "позавчера"},
    "vakar": {"translation": "вчера"},
    "šodien": {"translation": "сегодня"},
    "rīt": {"translation": "завтра"},
    "parīt": {"translation": "послезавтра"},
}
BORING_EMOJIS = ['🥱', '🙄', '😮‍💨', '😩', '😴', '😒', '😭', '💀', '💔']

NORMAL_LESSON_TIME = 40 * 60  # 40 minutes
SHORT_LESSON_TIME = 30 * 60   # 30 minutes
NORMAL_LESSON_TIMETABLE = {
    1: "08:10",
    2: "09:00",
    3: "09:55",
    4: "10:50",
    5: "11:45",
    6: "12:40",
    7: "13:30",
    8: "14:15",
    9: "15:00"
}
SHORT_LESSON_TIMETABLE = {
    1: "08:10",
    2: "08:50",
    3: "09:35",
    4: "10:20",
    5: "11:05",
    6: "12:40",
    7: "13:30",
    8: "14:15",
    9: "15:00"
}
