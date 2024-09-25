from aiogram.types import Message
from aiogram.filters import BaseFilter
from TelegramBot.settings import config
from data.async_database import UserDB


class UserModeFilter(BaseFilter):
    """
    Filter that checks if the user's chat mode matches the specified mode.

    :param mode: The mode to filter by (e.g., 'conference', 'news').
    """

    def __init__(self, mode: str):
        self.mode = mode

    async def __call__(self, message: Message) -> bool:
        """
        Checks the user's chat mode in the database and compares it with the desired mode.

        :param message: The incoming message to filter.
        :return: True if the user's mode matches the specified mode, False otherwise.
        """
        db = UserDB()
        await db.init()
        user_mode = await db.get_user_info(tg_id=message.from_user.id)
        user_mode = user_mode[0]['mode_chat']
        await db.close()

        return user_mode == self.mode


ADMIN_IDS = config.ADMINS_IDS


class IsAdmin(BaseFilter):
    """
    Filter that checks if the user is an admin by verifying their ID.
    """

    def __init__(self) -> None:
        self.admin_ids = ADMIN_IDS

    async def __call__(self, message: Message) -> bool:
        """
        Verifies if the user's ID is in the list of admin IDs.

        :param message: The incoming message to filter.
        :return: True if the user's ID is in the admin list, False otherwise.
        """
        return message.from_user.id in self.admin_ids
