import re

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from TelegramBot.conference_mode.conference_routers.gaianet_sql import chat_with_sql
from TelegramBot.middleware.middlewares import UserModeFilter
from TelegramBot.utils.log_message import log_message
from TelegramBot.utils.check_subscription import check_subscription
from TelegramBot.conference_mode.defs_conference import generate_msg_events
from TelegramBot.utils.coincidence import ContainsSubstringFilter
from TelegramBot.conference_mode.keyboards import builders
from TelegramBot.conference_mode.utils.pagination import PaginationEvent, paginator_event, get_msg_info_events, events_storage, events_storage_now_page, button_for_share_list
from TelegramBot.conference_mode.keyboards.builders import keyboard_for_add_or_remove_event
from TelegramBot.utils.states import FindList
from TelegramBot.utils.code_and_decode_key import code_secret_key, decode_secret_key

from data.async_database import ListEvents, Event, UserDB

# Initialize router for conference mode
router_conference = Router()
router_conference.message.filter(UserModeFilter(mode='conference'))

# Initialize database instances
EventDB = Event()
ListEventDB = ListEvents()
UserDB = UserDB()

@router_conference.callback_query(ContainsSubstringFilter('back_to_list_events'))
async def back_to_list_events(callback_query: CallbackQuery):
    """
    Handles returning to the list of events when 'Back to list' is clicked.
    """
    ids_events = events_storage[str(callback_query.from_user.id)]
    msg_and_buttons = await get_msg_info_events(list_ids_event=ids_events)
    msg = msg_and_buttons['msg']
    tg_id_user = callback_query.from_user.id
    now_page = events_storage_now_page[str(tg_id_user)]
    keyboard = await paginator_event(list_ids=ids_events, buttons=msg_and_buttons['buttons'], id_user=tg_id_user, page=now_page)
    return await callback_query.message.edit_text(text=msg, reply_markup=keyboard, disable_web_page_preview=True,
                                                  parse_mode=ParseMode.MARKDOWN)

@router_conference.callback_query(ContainsSubstringFilter('view_extened_info_event_'))
async def view_extened_info_about_event(callback_query: CallbackQuery):
    """
    Handles displaying extended information about a specific event.
    """
    id_event = int(callback_query.data.split('_')[-1])
    msg_text = await generate_msg_events.generate_extended_info_event(id_event=id_event)
    keyboard = await builders.keyboard_choice_for_add_in_list(id_event=id_event, tg_id=callback_query.from_user.id)
    return callback_query.message.edit_text(text=msg_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

@router_conference.callback_query(ContainsSubstringFilter('add_in_list_event_'))
async def add_in_list(callback_query: CallbackQuery):
    """
    Handles adding an event to a list when 'Add to list' is clicked.
    """
    tg_id = callback_query.from_user.id
    id_event = int(callback_query.data.split('_')[-1])
    msg = 'Choice list for adding event'
    keyboard = await builders.keyboard_choice_for_add_in_list(id_event=id_event, tg_id=tg_id)
    return await callback_query.message.edit_text(text=msg, reply_markup=keyboard)

@router_conference.callback_query(ContainsSubstringFilter('add_event_in_list_'))
async def add_event_in_list(callback_query: CallbackQuery):
    """
    Adds an event to the private list.
    """
    pattern = r"(?P<id_event>\d+)\*(?P<id_list>\d+)"
    id_event = re.search(pattern, callback_query.data).group('id_event')
    id_list = re.search(pattern, callback_query.data).group('id_list')
    await ListEventDB.add_event_in_private_list(id_event=id_event, id_list=id_list)
    keyboard = await keyboard_for_add_or_remove_event(id_event=id_event, tg_id=callback_query.from_user.id)
    return await callback_query.message.edit_text(text=callback_query.message.text, reply_markup=keyboard)

@router_conference.callback_query(ContainsSubstringFilter('remove_event_in_list_'))
async def remove_event_in_list(callback_query: CallbackQuery):
    """
    Removes an event from the private list.
    """
    pattern = r"(?P<id_event>\d+)\*(?P<id_list>\d+)"
    id_event = re.search(pattern, callback_query.data).group('id_event')
    id_list = re.search(pattern, callback_query.data).group('id_list')
    await ListEventDB.remove_event_from_private_list(id_event=id_event, id_list=id_list)
    keyboard = await keyboard_for_add_or_remove_event(id_event=id_event, tg_id=callback_query.from_user.id)
    return await callback_query.message.edit_text(text=callback_query.message.text, reply_markup=keyboard)

@router_conference.callback_query(ContainsSubstringFilter('show_info_list_'))
async def show_info_list(callback_query: CallbackQuery):
    """
    Displays information about a specific list of events.
    """
    pattern = r"(?P<id_list>\d+)\*(?P<type_list>)"
    id_list = re.search(pattern, callback_query.data).group('id_list')
    type_list = "public" if 'Pub' in callback_query.data else 'private'
    list_ids = await ListEventDB.get_list_event_ids_by_id_list(id_list=id_list, type_list=type_list)
    msg_and_keyboard = await generate_msg_events.generate_info_many_events(list_ids_events=list_ids[0]['event_ids'])
    msg = msg_and_keyboard['msg']
    keyboard = msg_and_keyboard['keyboard']
    return await callback_query.message.edit_text(text=msg, reply_markup=keyboard)

@router_conference.message(F.text == '🗂️My Events')
async def show_lists_events(message: Message):
    """
    Shows the list of private events for the user.
    """
    list_ids = await ListEventDB.get_privete_lists_events_by_tg_id(tg_id_user=message.from_user.id)
    list_ids = list_ids[0]['event_ids']
    msg_and_buttons = await get_msg_info_events(list_ids_event=list_ids)
    msg = msg_and_buttons['msg']
    keyboard = await paginator_event(list_ids=list_ids, buttons=msg_and_buttons['buttons'], id_user=message.from_user.id, my_list=True)
    new_button = InlineKeyboardButton(text='Share List', callback_data='share_my_private_list')
    keyboard.inline_keyboard.append([new_button])
    return await message.answer(text=msg, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@router_conference.message(F.text == '📜Side Events')
async def view_all_events(message: Message):
    """
    Displays all available side events.
    """
    list_events = await EventDB.get_all_events()
    list_ids = [event['id_event'] for event in list_events]
    msg_and_buttons = await get_msg_info_events(list_ids_event=list_ids)
    msg = msg_and_buttons['msg']
    keyboard = await paginator_event(list_ids=list_ids, buttons=msg_and_buttons['buttons'], id_user=message.from_user.id)
    return await message.answer(text=msg, reply_markup=keyboard, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)

@router_conference.message(F.text == '📖Categories')
async def find_by_tag(message: Message):
    """
    Prompts the user to select a category to search events by tag.
    """
    msg = 'Select a category'
    keyboard = await builders.events_by_tag()
    return await message.answer(text=msg, reply_markup=keyboard)

@router_conference.callback_query(ContainsSubstringFilter('find_events_by_tag_'))
async def find_event_by_tag(callback_query: CallbackQuery):
    """
    Searches for events based on a selected tag.
    """
    tags = callback_query.data.split('_')[-1].split('-')
    events = await EventDB.find_events_by_tag(tags=tags)
    events_id = [event['id_event'] for event in events]
    msg_and_buttons = await get_msg_info_events(list_ids_event=events_id)
    msg = msg_and_buttons['msg']
    keyboard = await paginator_event(list_ids=events_id, buttons=msg_and_buttons['buttons'], id_user=callback_query.from_user.id)
    return await callback_query.message.edit_text(text=msg, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@router_conference.callback_query(ContainsSubstringFilter('share_my_private_list'))
async def share_my_private_list(callback_query: CallbackQuery):
    """
    Shares the user's private event list via a generated key.
    """
    tg_id = callback_query.from_user.id
    list_event = await ListEventDB.get_privete_lists_events_by_tg_id(tg_id_user=tg_id)
    secret_key = code_secret_key(key=int(list_event[0]['key']))
    msg = f"""
Your key for sharing the list: `{secret_key}`
Click to copy"""
    await callback_query.message.answer(text=msg, parse_mode=ParseMode.MARKDOWN)

@router_conference.callback_query(ContainsSubstringFilter('add_list_in_my_favorit_'))
async def add_list_in_favorit(callback_query: CallbackQuery):
    """
    Adds the selected list to the user's favorites.
    """
    list_id = int(callback_query.data.split('_')[-1])
    user_id = await UserDB.get_id_by_tg_id(tg_id=callback_query.from_user.id)

@router_conference.message(F.text == '🔎Find list')
async def find_list(message: Message, state: FSMContext):
    """
    Prompts the user to enter a key to find a list.
    """
    msg = 'Enter key'
    await state.set_state(FindList.key)
    return await message.answer(text=msg)
