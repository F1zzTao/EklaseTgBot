import aiosqlite
from loguru import logger

from config import DB_PATH

CHAT_TABLE_SQL = """CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL UNIQUE,
    is_subscribed INTEGER NOT NULL DEFAULT 0
);"""


async def create_tables():
    logger.info("Creating tables")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CHAT_TABLE_SQL)
        await db.commit()
