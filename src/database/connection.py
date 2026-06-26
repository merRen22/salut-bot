import aiosqlite
import os


class DatabaseManager:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "data/salutbot.db")
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self):
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._create_tables()

    async def _create_tables(self):
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                min_words INTEGER NOT NULL DEFAULT 15,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                corrected_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        """)
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._conn
