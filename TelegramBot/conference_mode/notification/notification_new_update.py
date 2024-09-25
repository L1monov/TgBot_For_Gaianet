import asyncio
from aiogram import Router, Bot, F
from aiogram.types.callback_query import CallbackQuery
from aiogram.enums.parse_mode import ParseMode

from TelegramBot.conference_mode.utils.pagination import PaginationEvent, paginator_event, get_msg_info_events, \
    events_storage
from data.async_database import ParsingDB, UserDB, ListEvents
from TelegramBot.conference_mode.notification.keyboard_event_update import keyboard_for_updated_events

database = ParsingDB()
ListEventDB = ListEvents()
router = Router()

# Temporary storage for updated events to send to users
temp_dict_for_keyboard_updated_events = {}


async def get_dict_for_send_update_events():
    """
    Retrieves a dictionary of users and the updated events they have in their private lists.

    :return: Dictionary where key is the user ID and value is a list of updated event IDs
    """
    updated_events = await database.get_last_update_event(hours=5)
    users = await ListEventDB.get_all_private_lists()

    # Extract event IDs from updated events
    updated_events = [event['id_event'] for event in updated_events]

    notifications = {}

    for user in users:
        events = [int(id_event) for id_event in user['event_ids'].split(',')]
        matching_events = list(set(events) & set(updated_events))

        if matching_events:
            notifications[user['id_user']] = matching_events

    return notifications


async def send_notication(bot: Bot):
    """
    Sends a notification to users if there are any updated events from their private list.

    :param bot: Instance of the bot used to send notifications
    """
    user = UserDB()
    dict_notification = await get_dict_for_send_update_events()

    if dict_notification:
        for user_dict in dict_notification:
            id_for_send = await user.get_info_by_id(id_user=int(user_dict))
            tg_id_for_send = id_for_send[0]['tg_id']
            id_for_send = id_for_send[0]['id_user']

            id_events_for_send = dict_notification[str(id_for_send)]
            temp_dict_for_keyboard_updated_events[int(tg_id_for_send)] = id_events_for_send
            keyboard = await keyboard_for_updated_events()

            msg = f"""{len(id_events_for_send)} events from your list updated"""
            await bot.send_message(chat_id=tg_id_for_send, text=msg, reply_markup=keyboard)


@router.callback_query(F.data == 'view_about_updated_events')
async def view_about_new_events(callback_query: CallbackQuery):
    """
    Displays updated events when the user clicks on the 'Show updated events' button.

    :param callback_query: Callback query from the user
    """
    id_events_for_send = temp_dict_for_keyboard_updated_events[callback_query.from_user.id]

    msg_and_buttons = await get_msg_info_events(list_ids_event=id_events_for_send)
    keyboard = await paginator_event(list_ids=id_events_for_send, buttons=msg_and_buttons['buttons'],
                                     id_user=callback_query.from_user.id)
    msg = msg_and_buttons['msg']

    await callback_query.message.edit_text(text=msg, reply_markup=keyboard, disable_web_page_preview=True,
                                           parse_mode=ParseMode.MARKDOWN)


async def start_check_update_events(bot: Bot):
    """
    Periodically checks for updated events and sends notifications to users if necessary.

    :param bot: Instance of the bot used to send notifications
    """
    while True:
        await asyncio.sleep(14400)  # Check every 4 hours
        await send_notication(bot=bot)
