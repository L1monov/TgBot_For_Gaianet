from aiogram.types import Message
from aiogram import Router

from TelegramBot.middleware.middlewares import IsAdmin
from TelegramBot.utils.log_message import log_message

from data.async_database import AdminDB

# Initialize the router and AdminDB instance
router = Router()
AdminDB = AdminDB()


@router.message(IsAdmin(), lambda message: message.text.lower() == 'count users')
async def get_count_user(message: Message):
    """
    Handle 'count users' command for admin users.

    This function retrieves the total number of users from the database
    and sends the count as a response to the admin.

    :param message: The message object from the Telegram user (admin)
    """
    count_user = await AdminDB.get_count_user()
    msg = f"Count users: {count_user}"
    return await message.answer(text=msg)


@router.message(IsAdmin(), lambda message: message.text.lower() == 'average request')
@log_message()
async def get_average_request(message: Message):
    """
    Handle 'average request' command for admin users.

    This function retrieves the average number of requests per user
    from the database and sends the result as a response to the admin.

    :param message: The message object from the Telegram user (admin)
    """
    average_request = await AdminDB.get_average_requests_users()

    msg = f'Average requests: {average_request}'

    return await message.answer(text=msg)