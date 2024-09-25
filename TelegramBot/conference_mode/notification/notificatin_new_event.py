import asyncio
from aiogram import Router, Bot, F
from aiogram.types.callback_query import CallbackQuery
from aiogram.enums.parse_mode import ParseMode

from TelegramBot.conference_mode.utils.pagination import paginator_event, get_msg_info_events
from data.async_database import ParsingDB, UserDB, ListEvents
from TelegramBot.conference_mode.notification import keyboards


database = ParsingDB()
ListEventDB = ListEvents()
router = Router()


async def send_notication(bot: Bot):
    """
    Sends a notification to all users about new events if any were added in the last 5 hours.

    :param bot: Instance of the bot for sending messages
    """
    new_events = await database.get_last_add_events(hours=5)
    count_events = await database.get_count_events()
    print('New event', new_events)
    user = UserDB()

    if new_events:
        keyboard = await keyboards.keyboard_for_view_all_new_events()
        ids_for_send = await user.get_all_users()
        ids_for_send = [user['tg_id'] for user in ids_for_send]

        msg = f"""New KBW events detected 👀

New events: {len(new_events)}
Events in database: {count_events}"""

        for id_user in ids_for_send:
            try:
                await bot.send_message(chat_id=id_user, text=msg, reply_markup=keyboard)
            except Exception as ex:
                print(f"{ex}")
    else:
        return


@router.callback_query(F.data == 'view_about_new_events')
async def view_about_new_events(callback_query: CallbackQuery):
    """
    Handles the callback to display details about newly added events.

    :param callback_query: Callback query triggered when user clicks 'Show new events'
    """
    new_events = await database.get_last_add_events(hours=24)
    list_ids = [event['id_event'] for event in new_events]

    msg_and_buttons = await get_msg_info_events(list_ids_event=list_ids)
    msg = msg_and_buttons['msg']
    id_user = callback_query.from_user.id
    keyboard = await paginator_event(list_ids=list_ids, buttons=msg_and_buttons['buttons'], id_user=id_user)

    if new_events:
        await callback_query.message.edit_text(text=msg, reply_markup=keyboard, disable_web_page_preview=True,
                                               parse_mode=ParseMode.MARKDOWN)
    else:
        await callback_query.message.edit_text(text='No new events')


async def start_check_new_event(bot: Bot):
    """
    Continuously checks for new events and sends notifications if any are found.

    :param bot: Instance of the bot for sending notifications
    """
    while True:
        await send_notication(bot=bot)
        await asyncio.sleep(14000)
