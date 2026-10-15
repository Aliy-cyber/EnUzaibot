import aiosqlite

DB_NAME = "dictionary_cache.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                word TEXT PRIMARY KEY,
                response_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def get_cached_word(word: str) -> str | None:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT response_text FROM cache WHERE word = ?", (word.lower().strip(),)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def save_to_cache(word: str, response_text: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO cache (word, response_text) VALUES (?, ?)",
            (word.lower().strip(), response_text)
        )
        await db.commit()
