from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from TelegramBot.conference_mode.utils.pagination import PaginationEvent, paginator_event, get_msg_info_events, \
    events_storage
from TelegramBot.utils.coincidence import ContainsSubstringFilter
from data.async_database import Event


# State management class for finding main events
class FindMainEvents(StatesGroup):
    location = State()  # State for storing the location
    date = State()  # State for storing the selected date


# Dictionary for mapping dates to their shorthand
day_dict = {
    '3 Sep': '03Sep',
    '4 Sep': '04Sep'
}


async def keyboard_for_choice_day():
    """
    Generates an inline keyboard for choosing a day from the `day_dict`.

    :return: Inline keyboard markup with day choices
    """
    builder = InlineKeyboardBuilder()
    for day in day_dict:
        builder.add(InlineKeyboardButton(text=day, callback_data=f'find_by_day_{day_dict[day]}'))
    builder.adjust(2)
    return builder.as_markup()


# Dictionary for mapping locations
location_dict = {
    'Movement Stage': 'Movement Stage',
    'Sui Stage': 'Sui Stage',
    'Institutional Stage': 'Institutional Stage'
}


async def keyboard_find_main_events():
    """
    Generates an inline keyboard for selecting days and locations for the main event.

    :return: Inline keyboard markup with options for days and stages
    """
    builder = InlineKeyboardBuilder()

    # Row 1: Day selection buttons
    list_buttons = [
        InlineKeyboardButton(text=day, callback_data=f'find_by_day_{day_dict[day]}')
        for day in day_dict
    ]
    builder.row(*list_buttons)

    # Row 2: "Stages" button
    builder.row(InlineKeyboardButton(text='Stages 👇', callback_data='emply'))

    # Row 3 & 4: Location selection buttons
    list_buttons = [
        InlineKeyboardButton(text=location, callback_data=f'find_by_location_{location_dict[location]}')
        for location in location_dict
    ]
    builder.row(list_buttons[0], list_buttons[1])  # Row 3
    builder.row(list_buttons[2])  # Row 4

    return builder.as_markup()


# Initialize the router and event database instance
router_source_main_events = Router()
eventDB = Event()


@router_source_main_events.message(F.text == '📜Main Event Agenda')
async def source_main_events(message: Message):
    """
    Handles the user's request to see the main event agenda.

    Displays a selection keyboard for choosing a day or stage.

    :param message: Message object containing the user's request
    """
    msg = 'Select'
    keyboard = await keyboard_find_main_events()
    return await message.answer(text=msg, reply_markup=keyboard)


@router_source_main_events.callback_query(ContainsSubstringFilter('find_by_day_'))
async def find_main_event_by_day(callback_query: CallbackQuery):
    """
    Finds main events based on the selected day.

    :param callback_query: CallbackQuery object containing the user's selected day
    """
    day = callback_query.data.split('_')[-1]
    events = await eventDB.main_events_find_by_day(day=day)

    # Extract event IDs and generate the message with pagination
    list_ids_events = [event['id_event'] for event in events]
    msg_and_buttons = await get_msg_info_events(list_ids_event=list_ids_events)
    msg = msg_and_buttons['msg']

    keyboard = await paginator_event(list_ids=list_ids_events, buttons=msg_and_buttons['buttons'],
                                     id_user=callback_query.from_user.id)
    return await callback_query.message.edit_text(text=msg, reply_markup=keyboard, disable_web_page_preview=True,
                                                  parse_mode=ParseMode.MARKDOWN)


@router_source_main_events.callback_query(ContainsSubstringFilter('find_by_location_'))
async def find_main_event_by_location(callback_query: CallbackQuery, state: FSMContext):
    """
    Finds main events based on the selected location and then prompts the user to choose a day.

    :param callback_query: CallbackQuery object containing the user's selected location
    :param state: FSMContext to store the selected location and manage state
    """
    location = callback_query.data.split('_')[-1]
    await state.update_data(location=location)  # Store the selected location in the state
    await state.set_state(FindMainEvents.date)  # Set the state to expect a day choice
    keyboard = await keyboard_for_choice_day()
    await callback_query.message.edit_text(text='Select day', reply_markup=keyboard)


@router_source_main_events.callback_query(ContainsSubstringFilter('find_by_day_'), FindMainEvents.date)
async def find_loc_and_day(callback_query: CallbackQuery, state: FSMContext):
    """
    Finds main events based on the previously selected location and day.

    :param callback_query: CallbackQuery object containing the user's selected day
    :param state: FSMContext to retrieve both location and day for event filtering
    """
    await state.update_data(date=callback_query.data.split('_')[-1])  # Store the selected day in the state
    data_state = await state.get_data()

    # Retrieve events based on location and day from the state
    events = await eventDB.main_events_find_by_location_and_day(location=data_state['location'], day=data_state['date'])

    # Extract event IDs and generate the message with pagination
    list_ids_events = [event['id_event'] for event in events]
    msg_and_buttons = await get_msg_info_events(list_ids_event=list_ids_events)
    msg = msg_and_buttons['msg']

    keyboard = await paginator_event(list_ids=list_ids_events, buttons=msg_and_buttons['buttons'],
                                     id_user=callback_query.from_user.id)
    return await callback_query.message.edit_text(text=msg, reply_markup=keyboard, disable_web_page_preview=True,
                                                  parse_mode=ParseMode.MARKDOWN)
