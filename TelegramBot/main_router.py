from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router, Bot
from aiogram.enums.parse_mode import ParseMode

from data.async_database import UserDB, ListEvents
from TelegramBot.conference_mode.keyboards.builders import admin_keyboard
from TelegramBot.utils.log_message import log_message
from TelegramBot.middleware.middlewares import IsAdmin
from TelegramBot.utils.check_subscription import check_subscription
from TelegramBot.settings import config_texts
from TelegramBot.conference_mode.keyboards.builders import main_keyboard_conference_mode

router = Router()
User = UserDB()

@router.message(Command(commands=['chat']))
async def set_mode_chat(message: Message):
    """
    Command handler to set the user's mode to 'chat' mode.

    :param message: Incoming message from the user.
    :return: Confirmation message that 'Chat Mode' is active.
    """
    await User.set_mode_user(tg_id_user=message.from_user.id, mode_chat='chat')
    return await message.answer('Chat Mode')

@router.message(lambda message: message.text.lower() == 'conference mode')
@router.message(Command(commands=['conference']))
@check_subscription()
async def set_mode_conference(message: Message, bot: Bot):
    """
    Command handler to set the user's mode to 'conference' mode.
    Users can ask questions related to the conference agenda and side events.

    :param message: Incoming message from the user.
    :param bot: Bot instance.
    :return: Confirmation message that 'Conference Mode' is active along with the main conference keyboard.
    """
    await User.set_mode_user(tg_id_user=message.from_user.id, mode_chat='conference')
    keyboard = await main_keyboard_conference_mode()
    return await message.answer('Conference mode.\nAsk me questions about agenda and side events of KBW', reply_markup=keyboard)

@router.message(Command(commands=["start"]))
@check_subscription()
async def start(message: Message, bot: Bot):
    """
    Command handler to initiate the bot and set up the user's profile.
    It ensures the user has a private list of events and inserts them into the database if they are new.

    :param message: Incoming message from the user.
    :param bot: Bot instance.
    :return: Two welcome messages introducing the bot.
    """
    list_events = ListEvents()
    tg_id = message.from_user.id
    tg_username = message.from_user.username

    await list_events.check_private_list_user_and_create_if_none(tg_id_user=tg_id, username=tg_username)
    await User.insert_new_user(tg_id=tg_id, tg_username=tg_username)

    reply_reply = await main_keyboard_conference_mode()
    await message.answer(text=config_texts.msg_for_start_1, reply_markup=reply_reply, parse_mode=ParseMode.MARKDOWN)
    return await message.answer(text=config_texts.msg_for_start_2, parse_mode=ParseMode.MARKDOWN)

@router.message(IsAdmin(), Command(commands=['admin']))
@check_subscription()
@log_message()
async def admin(message: Message, bot: Bot):
    """
    Command handler for admins to access the admin menu.
    Only users with admin rights can access this command.

    :param message: Incoming message from the user.
    :param bot: Bot instance.
    :return: Admin menu with keyboard options.
    """
    msg = 'Admin menu'
    keyboard = await admin_keyboard()
    return await message.answer(msg, reply_markup=keyboard)
