from aiogram.types import Message

from functools import wraps

from data.async_database import AsyncDataBase
def log_message():
    db = AsyncDataBase()
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):

            try:
                response = await func(message, *args, **kwargs)
                # Логирование успешного ответа
                await db.log_message(user_id=message.from_user.id, username=message.from_user.username,
                                     message_text=message.text, response_text=response, error_message=None)
                return response
            except Exception as ex:
                # Логирование ошибки
                await db.log_message(user_id=message.from_user.id, username=message.from_user.username,
                                     message_text=message.text, response_text=None, error_message=str(ex))
                raise ex
        return wrapper
    return decorator