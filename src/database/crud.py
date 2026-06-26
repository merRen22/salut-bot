from typing import Any

import aiosqlite


async def get_user(conn: aiosqlite.Connection, telegram_id: int) -> dict[str, Any] | None:
    cursor = await conn.execute(
        "SELECT telegram_id, name, min_words, is_active FROM users WHERE telegram_id = ?",
        (telegram_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_active_user(conn: aiosqlite.Connection, telegram_id: int) -> dict[str, Any] | None:
    cursor = await conn.execute(
        "SELECT telegram_id, name, min_words, is_active FROM users WHERE telegram_id = ? AND is_active = 1",
        (telegram_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def create_user(
    conn: aiosqlite.Connection,
    telegram_id: int,
    name: str,
    min_words: int = 15,
    is_active: bool = True,
):
    await conn.execute(
        "INSERT INTO users (telegram_id, name, min_words, is_active) VALUES (?, ?, ?, ?)",
        (telegram_id, name, min_words, is_active),
    )
    await conn.commit()


async def update_user(
    conn: aiosqlite.Connection,
    telegram_id: int,
    name: str | None = None,
    min_words: int | None = None,
    is_active: bool | None = None,
):
    fields = []
    values = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if min_words is not None:
        fields.append("min_words = ?")
        values.append(min_words)
    if is_active is not None:
        fields.append("is_active = ?")
        values.append(is_active)
    if not fields:
        return
    values.append(telegram_id)
    await conn.execute(
        f"UPDATE users SET {', '.join(fields)} WHERE telegram_id = ?",
        values,
    )
    await conn.commit()


async def get_all_users(conn: aiosqlite.Connection) -> list[dict[str, Any]]:
    cursor = await conn.execute("SELECT telegram_id, name, min_words, is_active FROM users")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def save_progress(
    conn: aiosqlite.Connection,
    telegram_id: int,
    message: str,
    word_count: int,
    corrected_text: str | None = None,
):
    await conn.execute(
        "INSERT INTO progress (telegram_id, message, word_count, corrected_text) VALUES (?, ?, ?, ?)",
        (telegram_id, message, word_count, corrected_text),
    )
    await conn.commit()
