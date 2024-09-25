from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from data.async_database import Event
from TelegramBot.conference_mode.defs_conference import generate_msg_events

events_storage = {}
events_storage_now_page = {}


class PaginationEvent(CallbackData, prefix="pag_event"):
    """
    Callback data class for handling pagination events.
    """
    action: str
    page: int
    key: str
    count_event: int
    tag: str = 'test'
    my_list: int = 0


async def paginator_event(list_ids: str | list, buttons: list, id_user: int, page: int = 0, my_list: bool = False):
    """
    Creates a pagination inline keyboard for event navigation.

    :param list_ids: List or comma-separated string of event IDs
    :param buttons: List of InlineKeyboardButton objects
    :param id_user: Telegram user ID
    :param page: Current page number
    :param my_list: Boolean flag indicating if it's the user's private list
    :return: InlineKeyboardMarkup for paginated events
    """
    if isinstance(list_ids, str):
        list_ids_1 = list_ids.split(',')
    else:
        list_ids_1 = list_ids

    event = Event()
    events = await event.get_info_many_events(list_ids_events=list_ids_1)
    count_event = len(events)
    key = str(id_user)
    events_storage[key] = list_ids_1
    events_storage_now_page[key] = page

    builder = InlineKeyboardBuilder()
    [builder.add(button) for button in buttons]

    prev_callback_data = PaginationEvent(action='prev_events', page=page, key=key, count_event=count_event,
                                         my_list=int(my_list)).pack()
    next_callback_data = PaginationEvent(action='next_events', page=page, key=key, count_event=count_event,
                                         my_list=int(my_list)).pack()

    builder.row(
        InlineKeyboardButton(text='⬅', callback_data=prev_callback_data),
        InlineKeyboardButton(text=f"{page + 1}/{(count_event + 4) // 5}", callback_data='None'),
        InlineKeyboardButton(text='➡', callback_data=next_callback_data),
        width=3
    )
    return builder.as_markup()


async def get_msg_info_events(list_ids_event: str | list, skip: int = 0, limit: int = 5):
    """
    Generates a message and buttons for displaying event information.

    :param list_ids_event: List or comma-separated string of event IDs
    :param skip: Number of events to skip for pagination
    :param limit: Maximum number of events to display
    :return: Dictionary containing the message and associated buttons
    """
    if isinstance(list_ids_event, str):
        list_ids_event = list_ids_event.split(',')

    event = Event()
    list_events = await event.get_info_many_events(list_ids_events=list_ids_event)

    msg = f'Events found: {len(list_events)}\n'
    list_events = list_events[skip:limit]
    buttons = []
    pagination_event = 1
    pagination_event_emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

    if len(list_ids_event) == 1:
        id_event = list_events[0]['id_event']
        msg = await generate_msg_events.generate_extended_info_event(id_event=id_event)
        buttons.append(
            InlineKeyboardButton(text=pagination_event_emoji[0], callback_data=f'view_extened_info_event_{id_event}'))
    else:
        for event in list_events:
            name_event = event['name_event']
            date_event = event['date_event']
            location = event['location_event']
            url_location = f"https://www.google.com/maps/search/?api=1&query={location.replace(' ', '+')}"
            host = event['host_event'].replace(',', ', ')
            event_page = event['url_event']
            time_event = event['time_event']

            msg += f"""
{pagination_event_emoji[pagination_event - 1]} *{name_event}*
🕒*Date*: {date_event if date_event else 'not indicated'} {time_event}
📍*Location*: [{location}]({url_location})
⭐*Host*: {host if host else 'not indicated'}
🌐*Event Page*: [Link]({event_page})
"""
            buttons.append(InlineKeyboardButton(text=pagination_event_emoji[pagination_event - 1],
                                                callback_data=f'view_extened_info_event_{event["id_event"]}'))
            pagination_event += 1

    msg += "❤️ Save event into favourites by pressing the corresponding button below."
    return {'msg': msg, 'buttons': buttons}


async def button_for_share_list(builder):
    """
    Adds a 'Share List' button to the inline keyboard builder.

    :param builder: InlineKeyboardBuilder object
    :return: InlineKeyboardBuilder with 'Share List' button added
    """
    builder.append(InlineKeyboardButton(text='Share List', callback_data='share_my_private_list'))
    return builder
