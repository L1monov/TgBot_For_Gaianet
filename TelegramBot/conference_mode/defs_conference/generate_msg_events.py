from TelegramBot.conference_mode.keyboards.builders import keyboard_for_view_extended_info_events
from data.async_database import Event
from TelegramBot.conference_mode.conference_routers.generate_short_description import generate_short_description

EventDB = Event()


async def generate_info_many_events(list_ids_events: str | list, skip: int = 0, page: int = 1):
    """
    Generates information for multiple events and formats it for message display,
    including pagination for large lists.

    :param list_ids_events: List or comma-separated string of event IDs
    :param skip: Number of events to skip for pagination
    :param page: Current page number for pagination
    :return: Dictionary containing the formatted message and keyboard
    """
    if isinstance(list_ids_events, str):
        list_ids_events = list_ids_events.split(',')

    events_dict = await EventDB.get_info_many_events(list_ids_events=list_ids_events)

    dict_for_keyboard_view_extended_info = []

    pagination_event_emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    msg = f'Find {len(events_dict)} events\n'
    pagination_event = 1

    if len(events_dict) < 10:
        for event in events_dict:
            name_event = event['name_event']
            date_event = event['date_event']
            location = event['location_event']
            host = event['host_event'].replace(',', ', ')
            event_page = event['url_event']

            msg += f"""
{pagination_event_emoji[pagination_event - 1]}) *{name_event}*
*Date*: {date_event if date_event else 'not indicated'}
*Location*: {location if location else 'not indicated'}
*Host*: {host if host else 'not indicated'}
*Event Page*: {event_page if event_page else 'not indicated'}

"""

            dict_for_keyboard_view_extended_info.append({
                'id_pagination': pagination_event,
                'id_event': event['id_event']
            })
            pagination_event += 1

        keyboard = await keyboard_for_view_extended_info_events(
            list_events=dict_for_keyboard_view_extended_info,
            str_list_ids_event=','.join(list_ids_events)
        )

        return {'msg': msg, 'keyboard': keyboard}

    else:
        events_to_msg = events_dict[skip:page * 5]

        for event in events_to_msg:
            name_event = event['name_event']
            date_event = event['date_event']
            location = event['location_event']
            host = event['host_event'].replace(',', ', ')
            event_page = event['url_event']

            msg += f"""
{pagination_event_emoji[pagination_event - 1]}) *{name_event}*
*Date*: {date_event if date_event else 'not indicated'}
*Location*: {location if location else 'not indicated'}
*Host*: {host if host else 'not indicated'}
*Event Page*: {event_page if event_page else 'not indicated'}
            """

            dict_for_keyboard_view_extended_info.append({
                'id_pagination': pagination_event,
                'id_event': event['id_event']
            })
            pagination_event += 1

        keyboard = await keyboard_for_view_extended_info_events(
            list_events=dict_for_keyboard_view_extended_info,
            str_list_ids_event=','.join(list_ids_events)
        )


async def generate_extended_info_event(id_event: int):
    """
    Generates detailed information for a specific event including an AI-generated summary.

    :param id_event: Event ID
    :return: Formatted message with event details and AI-generated summary
    """
    event_info = await EventDB.get_info_event_by_id(id_event=id_event)

    speakers = event_info['speakers_event']
    short_description = await generate_short_description(
        full_description=event_info['description_event']
    ) if event_info['description_event'] else 'The event has no description'

    msg = f"""*{event_info['name_event']}*
🕒*Date event*: {event_info['date_event']}
📍*Location event*: {event_info['location_event']}
⭐*Host event*: {event_info['host_event']}
🎙️*Speakers*: {speakers}

🌐*AI generated summary*: {short_description}
"""
    return msg