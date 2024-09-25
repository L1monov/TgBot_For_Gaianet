from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext

from TelegramBot.settings.config_texts import msg_for_start_1, msg_for_start_2
from TelegramBot.utils.check_subscription import check_subscription
from TelegramBot.conference_mode.keyboards import inline
from TelegramBot.conference_mode.keyboards.builders import main_keyboard_conference_mode
from TelegramBot.utils.states import EthCC_Main_Event

# Initialize the router
router = Router()


@router.callback_query(F.data == 'check_subcription')
@check_subscription()
async def start_tutorial(call: CallbackQuery):
    """
    Handles the 'check_subscription' callback query.

    This function first checks if the user is subscribed, then sends the first
    part of a tutorial message followed by the second part, using Markdown formatting.
    It also provides a keyboard for interacting in conference mode.

    :param call: CallbackQuery object representing the user's interaction
    """
    reply_reply = await main_keyboard_conference_mode()  # Load the main keyboard for conference mode
    await call.message.answer(text=msg_for_start_1, reply_markup=reply_reply, parse_mode=ParseMode.MARKDOWN)
    await call.message.answer(text=msg_for_start_2, parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data == 'Side events')
async def callback_list_event(callback_query: CallbackQuery):
    """
    Handles the 'Side events' callback query.

    This function sends a message asking the user what they are looking for and provides
    a keyboard with options to select different event tags.

    :param callback_query: CallbackQuery object representing the user's interaction
    """
    msg = 'What are you looking for?'
    keyboard = await inline.keyboard_for_all_event_select_tag()  # Load the keyboard for selecting event tags
    return await callback_query.message.answer(text=msg, reply_markup=keyboard)


@router.callback_query(F.data == 'EthCC Main Event')
async def main_event_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Handles the 'EthCC Main Event' callback query.

    This function sets the state to 'EthCC_Main_Event.day' and provides the user
    with a keyboard to select a specific day or topic for the main event.

    :param callback_query: CallbackQuery object representing the user's interaction
    :param state: FSMContext representing the current state in the finite state machine
    """
    await state.set_state(EthCC_Main_Event.day)  # Set the state to allow selecting a day or topic
    keyboards = await inline.select_day_main_event()  # Load the keyboard for selecting a day or topic
    await callback_query.message.answer(text='Select day or topic', reply_markup=keyboards)
