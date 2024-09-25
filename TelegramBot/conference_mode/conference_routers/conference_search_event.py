from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.enums.parse_mode import ParseMode

from TelegramBot.conference_mode.conference_routers.gaianet_sql import chat_with_sql
from TelegramBot.utils.log_message import log_message
from TelegramBot.utils.check_subscription import check_subscription
from TelegramBot.middleware.middlewares import UserModeFilter
from TelegramBot.conference_mode.utils.pagination import PaginationEvent, paginator_event, get_msg_info_events, \
    events_storage

# Initialize router for event search with the 'conference' mode filter
router_search_events = Router()
router_search_events.message.filter(UserModeFilter(mode='conference'))


@router_search_events.message(lambda message: not message.text.startswith("PB"))
@log_message()  # Log the message
@check_subscription()  # Check if the user has an active subscription
async def message_handler(message: Message, bot: Bot):
    """
    Handles user messages that are not starting with 'PB'.
    This function sends the user's query to OpenAI for SQL-based event search and returns paginated results.

    :param message: Message object from the user
    :param bot: Bot instance for sending messages
    """
    try:
        await message.answer('Searching... 🕵️')  # Send a loading message
        answer = await chat_with_sql(query=message.text)  # Query the events using OpenAI
        msg_and_buttons = await get_msg_info_events(list_ids_event=answer)  # Fetch event details
        msg = msg_and_buttons['msg']  # Get the message to be displayed
        keyboard = await paginator_event(list_ids=answer, buttons=msg_and_buttons['buttons'],
                                         id_user=message.from_user.id)  # Generate pagination buttons

        # Send the final response with the event details and pagination
        return await message.answer(text=msg, reply_markup=keyboard, disable_web_page_preview=True,
                                    parse_mode=ParseMode.MARKDOWN)
    except Exception as ex:
        # Handle errors and notify both the user and admin
        await message.answer(text='Error 🤖 Please specify your question or try asking in a different way.')
        await bot.send_message(chat_id=854686840, text=f'query: {message.text}')
        return await bot.send_message(chat_id=854686840, text=f'Error\n{ex}')


@log_message()  # Log callback queries for pagination
@router_search_events.callback_query(PaginationEvent.filter(F.action.in_(['prev_events', 'next_events'])))
async def pagination_for_all_list(call: CallbackQuery, callback_data: PaginationEvent):
    """
    Handles pagination for event lists. It adjusts the page number based on 'next' or 'previous' button clicks,
    retrieves the next set of events, and updates the message with the new page.

    :param call: CallbackQuery object from the user interaction
    :param callback_data: Data associated with the pagination event
    """
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 0 else 0  # Calculate the current page number

    if callback_data.action == 'next_events':
        # Calculate the next page, ensuring it does not exceed the maximum number of pages
        page = page_num + 1 if page_num < int(callback_data.count_event / 5) else page_num

    key = callback_data.key
    events_list = events_storage.get(key, [])  # Retrieve the list of events from storage

    # Fetch event details for the current page
    msg_and_buttons = await get_msg_info_events(list_ids_event=events_list, skip=page * 5, limit=page * 5 + 5)
    msg = msg_and_buttons['msg']  # Get the message content

    # Generate the appropriate keyboard depending on whether it's the user's list or not
    if callback_data.my_list:
        keyboard = await paginator_event(page=page, list_ids=events_list, buttons=msg_and_buttons['buttons'],
                                         id_user=call.from_user.id, my_list=True)
        new_button = InlineKeyboardButton(text='Share List', callback_data='share_my_private_list')
        keyboard.inline_keyboard.append([new_button])  # Add 'Share List' button if it's the user's list
    else:
        keyboard = await paginator_event(page=page, list_ids=events_list, buttons=msg_and_buttons['buttons'],
                                         id_user=call.from_user.id)

    # Update the message with the new events for the selected page
    await call.message.edit_text(text=msg, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN,
                                 disable_web_page_preview=True)
