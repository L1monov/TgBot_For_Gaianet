import asyncio
from aiogram import Dispatcher, Bot, Router
from aiogram.fsm.storage.memory import MemoryStorage

from TelegramBot.conference_mode.notification.notification_new_update import start_check_update_events
from TelegramBot.settings.config import BOT_TOKEN

from TelegramBot.conference_mode.handlers import main_handlers
from TelegramBot import main_router
from TelegramBot.conference_mode.conference_routers import conference
from TelegramBot.admin_mode import admin_router
from TelegramBot.conference_mode.callbacks import main_callbacks
from TelegramBot.middleware.antiflood import AntiFloodMiddleware
from TelegramBot.middleware.log_message import LoggingMiddleware
from TelegramBot.middleware.check_private_chat import PrivateChatFilterMiddleware

from TelegramBot.conference_mode.notification import notificatin_new_event
from TelegramBot.conference_mode.notification import notification_new_update
from TelegramBot.conference_mode.conference_routers.conference_search_event import router_search_events
from TelegramBot.conference_mode.conference_routers.conference_source_main_events import router_source_main_events
from TelegramBot.conference_mode.conference_routers.conference_find_list import router_find_list

router = Router()


async def main():
    """
    Main function to start the bot and handle notifications for new and updated events.
    This function gathers the bot's main execution loop and notification checks for new and updated events.
    """
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    await asyncio.gather(
        run_bot(bot=bot, dp=dp),
        notificatin_new_event.start_check_new_event(bot=bot),
        start_check_update_events(bot=bot)
    )


async def run_bot(bot: Bot, dp: Dispatcher):
    """
    Runs the bot, sets up middlewares, and includes all routers for handling commands and callbacks.

    :param bot: The bot instance to run.
    :param dp: The dispatcher instance to handle updates and middleware.
    """
    storage = MemoryStorage()
    dp["dp"] = dp
    dp["storage"] = storage

    # Adding middleware
    dp.message.middleware(PrivateChatFilterMiddleware())
    dp.message.middleware(AntiFloodMiddleware())
    dp.message.middleware(LoggingMiddleware())

    # Including routers for different bot functionalities
    dp.include_routers(
        router,
        main_router.router,
        admin_router.router,
        conference.router_conference,
        main_callbacks.router,
        router_source_main_events,
        notificatin_new_event.router,
        notification_new_update.router,
        router_search_events,
        router_find_list,
    )

    # Deleting webhook and starting polling
    await bot.delete_webhook(drop_pending_updates=True)
    print('Bot rolling')
    await dp.start_polling(bot)
