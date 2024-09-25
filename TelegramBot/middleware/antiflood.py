import asyncio
from time import time as timeSeconds
from typing import Any, Awaitable, Callable, Dict

from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.enums.parse_mode import ParseMode

class AntiFloodMiddleware(BaseMiddleware):
    """
    Middleware that prevents users from sending too many messages in a short period of time (anti-flood protection).
    If a user sends more than 9 messages in under a minute, they will be temporarily blocked for 1 minute.

    :dict_info: Stores the count of messages for each user to monitor the message rate.
    """
    dict_info = {}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message,
                       data: Dict[str, Any]) -> Any:
        """
        Intercepts the incoming message event, checks the rate of messages, and applies anti-flooding logic.

        :param handler: The next handler to call if the user is not flooding.
        :param event: The message event.
        :param data: Additional context data.
        :return: The result of the handler or a warning message if the user is flooding.
        """
        user_id = event.from_user.id
        time = timeSeconds()

        if not self.dict_info.get(user_id):
            self.dict_info[user_id] = 0

        asyncio.create_task(self.add_message(user_id=user_id))

        if self.dict_info[user_id] > 9:
            await event.answer(text='The bot is free so we ask you to cooldown for 1 minute and not to rug us 🤖')
            return

        return await handler(event, data)

    async def add_message(self, user_id: int) -> None:
        """
        Increments the message count for the user and resets it after 60 seconds.

        :param user_id: The ID of the user.
        """
        self.dict_info[user_id] += 1
        await asyncio.sleep(60)
        self.dict_info[user_id] -= 1
