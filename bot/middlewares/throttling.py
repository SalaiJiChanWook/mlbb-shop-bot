import time
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from config.settings import settings

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit_seconds: float = settings.RATE_LIMIT_SECONDS):
        super().__init__()
        self.limit = limit_seconds
        self.last_user_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            now = time.time()
            if user_id in self.last_user_time:
                delta = now - self.last_user_time[user_id]
                if delta < self.limit:
                    # Message ကို Ignore လုပ်ကာ Bot Token/Server Overload မဖြစ်အောင် တားဆီးခြင်း
                    return
            self.last_user_time[user_id] = now
            
        return await handler(event, data)