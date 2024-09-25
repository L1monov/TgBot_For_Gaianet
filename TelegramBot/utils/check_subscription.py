from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from TelegramBot.settings.config import GROUP_FOR_SUBCRIPTION
from functools import wraps


from TelegramBot.conference_mode.keyboards.builders import keyboard_check_subscription
from data.async_database import UserDB

def check_subscription():
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            bot = kwargs.get('bot')  # Получаем объект бота из kwargs
            # Логирование успешного ответа
            response = await func(message, *args, **kwargs)
            #
            return response
            # info_user = await bot.get_chat_member(chat_id=GROUP_FOR_SUBCRIPTION, user_id=message.from_user.id)
            # user = UserDB()
            # if info_user.status != 'left':
            #     user = UserDB()
            #     await user.insert_new_user(tg_id=message.from_user.id, tg_username=message.from_user.username)
            #     response = await func(message, *args, **kwargs)
            #     # Логирование успешного ответа
            #     return response
            # else:
            #     await user.insert_new_user(tg_id=message.from_user.id, tg_username=message.from_user.username)
            #     keyboards = keyboard_check_subscription()
            #     await message.answer('Our bot’s totally free, just here to make your life easier. If you’re vibing with it, do us a solid and join @cryptosummary_eth to get AI generated market updates.\nThanks for the support! 🙏', parse_mode=ParseMode.HTML, reply_markup=keyboards)
        return wrapper
    return decorator