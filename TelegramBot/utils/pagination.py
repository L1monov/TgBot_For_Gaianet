import asyncio

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from data.async_database import Event

class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int
    count_event: int = 0
    tag: str = 'test'

async def paginator(tag: str, page: int = 0):
    event = Event()
    count_event = len(await event.get_info_all_events_by_tag(tag=tag))
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅', callback_data=Pagination(action='prev', page=page, tag=tag, count_event=count_event).pack()),
        InlineKeyboardButton(text=f"{page+1}/{int(count_event/5)+1}", callback_data='None'),
        InlineKeyboardButton(text='➡', callback_data=Pagination(action='next', page=page, tag=tag, count_event=count_event).pack()),
        width=3
    )
    return builder.as_markup()

async def get_msg_info_events(tag: str, skip: int = 0, limit: int = 5):
    print('get_msg_info_events')
    event = Event()
    list_events = await event.get_info_all_events_by_tag(tag=tag)
    # Pagination.count_event = len(list_events)
    # Pagination.tag = tag
    print(list_events)
    list_events = list_events[skip:limit]
    print(list_events)
    msg = ''
    for event in list_events:
        msg += f"""`{event['name_event']}`
⏰{event['date_event']} {event['time_event']} [🔗 event page]({event['url_event']})

"""
    msg += f"👉press event name to copy"

    return {
        'msg_text': msg,
        "tag": tag
    }


