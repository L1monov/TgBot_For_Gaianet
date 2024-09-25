import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware

# Импорт вашей функции write_log
from data.async_database import LogsDB


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging messages and bot responses, including errors.
    Logs each user's message, the bot's response, and any errors that occur during processing.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message,
                       data: Dict[str, Any]) -> Any:
        """
        Intercepts and logs the user's message, the bot's response, and any errors that occur.

        :param handler: The next handler to call after logging the event.
        :param event: The message event being processed.
        :param data: Additional context data.
        :return: The result of the handler (bot's response) or error if any.
        """
        user_id = event.from_user.id
        username = event.from_user.username if event.from_user.username else 'No username'
        user_message = event.text

        try:
            # Process the message and capture the bot's response
            response = await handler(event, data)
            bot_response_text = response.text if response and hasattr(response, 'text') else 'No response text'
            error = None
        except Exception as e:
            # Log the error if one occurs
            response = None
            bot_response_text = 'No response due to error'
            error = str(e)

        # Log the user message, bot response, and any errors
        await self.log_message(user_id, user_message, bot_response_text, error, username=username)

        return response

    async def log_message(self, user_id: int, user_message: str, bot_response: str, error: str, username: str):
        """
        Logs the user message, bot response, and any errors to the database.

        :param user_id: The ID of the user sending the message.
        :param user_message: The content of the user's message.
        :param bot_response: The content of the bot's response.
        :param error: Any error that occurred during processing.
        :param username: The username of the user.
        """
        log = LogsDB()
        await log.log_message(user_id=user_id, username=username, message_text=user_message, response_text=bot_response, error_message=error)
