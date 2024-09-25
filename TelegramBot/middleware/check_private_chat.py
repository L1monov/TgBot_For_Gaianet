from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

class PrivateChatFilterMiddleware(BaseMiddleware):
    """
    Middleware that filters messages, allowing only messages from private chats to pass through.
    Messages from group or channel chats are ignored.
    """
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        """
        Processes incoming messages and allows only messages from private chats.

        :param handler: The next handler to call if the message is from a private chat.
        :param event: The message event being processed.
        :param data: Additional context data.
        :return: The result of the handler if the message is from a private chat, otherwise nothing.
        """
        if event.chat.type == 'private':
            return await handler(event, data)
        else:
            # Ignore messages that are not from private chats
            return
