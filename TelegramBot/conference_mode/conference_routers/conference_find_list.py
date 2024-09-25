from aiogram.types import Message
from aiogram import Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from TelegramBot.middleware.middlewares import UserModeFilter
from TelegramBot.conference_mode.utils.pagination import paginator_event, get_msg_info_events
from TelegramBot.utils.states import FindList
from TelegramBot.utils.code_and_decode_key import decode_secret_key

from data.async_database import ListEvents, Event, UserDB

# Initialize the router with a filter for the 'conference' mode
router_find_list = Router()
router_find_list.message.filter(UserModeFilter(mode='conference'))

# Initialize database instances
EventDB = Event()
ListEventDB = ListEvents()
UserDB = UserDB()


@router_find_list.message(FindList.key)
async def find_list_by_key(message: Message, state: FSMContext):
    """
    Handles the event list search by a secret key provided by the user.

    The function decodes the provided key, retrieves the associated event list, and displays
    the list's information with navigation buttons for the user. It also allows users to add
    or remove the list from their favorites.

    :param message: The message object containing the user's input
    :param state: FSMContext for managing the state of the conversation
    """
    try:
        # Remove 'PB' from the key and decode it
        key = message.text.replace('PB', '')
        key = decode_secret_key(key=int(key))
        # Fetch the event list by the decoded secret key
        list_event = await ListEventDB.get_list_by_secret_key(key=key)
    except:
        list_event = 0

    # If the list is not found, prompt the user to enter a key again
    if not list_event:
        return await message.answer(text='Not found, please enter again')

    # Extract event IDs from the list and get the event information
    list_ids = list_event[0]['event_ids']
    msg_and_buttons = await get_msg_info_events(list_ids_event=list_ids)

    # Extract list ID and message to be displayed
    list_id = list_event[0]['id_list']
    msg = msg_and_buttons['msg']

    # Generate pagination keyboard with event details
    keyboard = await paginator_event(list_ids=list_ids, buttons=msg_and_buttons['buttons'],
                                     id_user=message.from_user.id)

    # Check if the event list is already in the user's favorites
    info_user_favorite_private_lists = await UserDB.get_favorite_private_list_by_user_id(id_user=message.from_user.id)
    list_favorite_users = info_user_favorite_private_lists[0]['favorites_private_lists']

    # Add a button to add or remove the list from the user's favorites
    if str(list_id) in str(list_favorite_users).split(','):
        button_to_favorit = InlineKeyboardButton(text='Delete from my favorites',
                                                 callback_data=f'delete_list_in_my_favorit_{list_id}')
        keyboard.inline_keyboard.append([button_to_favorit])
    else:
        button_to_favorit = InlineKeyboardButton(text='Add in my favorites',
                                                 callback_data=f'add_list_in_my_favorit_{list_id}')
        keyboard.inline_keyboard.append([button_to_favorit])

    # Clear the state and send the final message with the generated keyboard
    await state.clear()
    return await message.answer(text=msg, reply_markup=keyboard, disable_web_page_preview=True,
                                parse_mode=ParseMode.MARKDOWN)
