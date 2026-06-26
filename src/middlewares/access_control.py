from typing import Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from src.database.connection import DatabaseManager
from src.database.crud import get_active_user


class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            if user_id is None:
                return
            user = await get_active_user(self.db_manager.conn, user_id)
            if user is None:
                return
            data["user"] = user
        return await handler(event, data)
