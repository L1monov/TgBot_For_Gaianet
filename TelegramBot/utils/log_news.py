import time
from aiogram.types import Message
from functools import wraps
from data.async_database import AsyncDataBase

def log_news():
    db = AsyncDataBase()
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__  # Получаем название функции
            start_time = time.time()   # Засекаем время начала
            try:
                response = await func(*args, **kwargs)
                end_time = time.time()  # Засекаем время конца
                execution_time = end_time - start_time  # Рассчитываем время выполнения
                execution_time = f"{execution_time:.2f}"  # Форматируем время выполнения в секунды
                # Логирование успешного ответа
                await db.log_news(action=func_name, response=response, error=None, execution_time=execution_time)
                return response
            except Exception as ex:
                end_time = time.time()  # Засекаем время конца даже при ошибке
                execution_time = end_time - start_time  # Рассчитываем время выполнения
                execution_time = f"{execution_time:.2f}"  # Форматируем время выполнения в секунды
                # Логирование ошибки
                await db.log_news(action=func_name, response=None, error=f"{ex}", execution_time=execution_time)
                raise ex
        return wrapper
    return decorator
